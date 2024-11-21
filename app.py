from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from sqlalchemy.exc import ProgrammingError
from sqlalchemy import inspect, text

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/mydatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


# Define the table model
class MyTable(db.Model):
    __tablename__ = 'mytable'
    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    data = db.Column(db.String(255))



@app.route('/', methods=["GET"])
def home_page():
    return "Hello World"


@app.route('/check-database', methods=['GET'])
def check_database():
    try:
        # Try to execute a simple query to check database existence
        db.session.execute(text('SELECT 1'))
        return jsonify({"message": "Database 'mydatabase' exists and is accessible"})
    except ProgrammingError:
        # If database doesn't exist, create it
        db.create_all()
        return jsonify({"message": "Database 'mydatabase' was created"})


# be able to call 
@app.route('/check-table', methods=['GET'])
def check_table():
    inspector = inspect(db.engine)
    if 'mytable' in inspector.get_table_names():
        return jsonify({"message": "Table 'mytable' exists"})
    else:
        db.create_all()
        return jsonify({"message": "Table 'mytable' was created"})


@app.route('/add-data', methods=['POST'])
def add_data():
    data = request.json.get('data')
    if not data:
        return jsonify({"error": "No data provided"}), 400

    new_entry = MyTable(data=data)
    db.session.add(new_entry)
    db.session.commit()

    return jsonify({
        "message": "Data added successfully",
        "uuid": new_entry.uuid,
        "data": new_entry.data
    })


@app.route('/get-all', methods=['GET'])
def get_all():
    entries = MyTable.query.all()
    return jsonify([{
        "uuid": entry.uuid,
        "data": entry.data
    } for entry in entries])


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
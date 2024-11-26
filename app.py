from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from sqlalchemy.exc import ProgrammingError
from sqlalchemy import inspect, text
import logging
from logging.handlers import TimedRotatingFileHandler

# Initialize the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# File handler for all logs
file_handler = TimedRotatingFileHandler('app.log', when='midnight', interval=1)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

# Stream handler for INFO logs
info_stream_handler = logging.StreamHandler()
info_stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
info_stream_handler.setLevel(logging.INFO)
info_stream_handler.addFilter(logging.Filter('INFO'))
logger.addHandler(info_stream_handler)

# Stream handler for WARN logs
warn_stream_handler = logging.StreamHandler()
warn_stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
warn_stream_handler.setLevel(logging.WARNING)
warn_stream_handler.addFilter(logging.Filter('WARNING'))
logger.addHandler(warn_stream_handler)

# Stream handler for ERROR logs
error_stream_handler = logging.StreamHandler()
error_stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
error_stream_handler.setLevel(logging.ERROR)
error_stream_handler.addFilter(logging.Filter('ERROR'))
logger.addHandler(error_stream_handler)

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/mydatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Define the table model
class MyTable(db.Model):
    __tablename__ = 'mytable'
    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    data = db.Column(db.String(255))


@app.route('/check-database', methods=['GET'])
def check_database():
    try:
        db.session.execute(text('SELECT 1'))
        logger.info("Checked database connectivity successfully.")
        return jsonify({"message": "Database 'mydatabase' exists and is accessible"})
    except ProgrammingError:
        db.create_all()
        logger.warning("Database 'mydatabase' was created as it did not exist.")
        return jsonify({"message": "Database 'mydatabase' was created"})

@app.route('/check-table', methods=['GET'])
def check_table():
    inspector = inspect(db.engine)
    if 'mytable' in inspector.get_table_names():
        logger.info("Table 'mytable' exists.")
        return jsonify({"message": "Table 'mytable' exists"})
    else:
        db.create_all()
        logger.warning("Table 'mytable' was created as it did not exist.")
        return jsonify({"message": "Table 'mytable' was created"})

@app.route('/add-data', methods=['POST'])
def add_data():
    data = request.json.get('data')
    if not data:
        logger.error("No data provided in /add-data endpoint.")
        return jsonify({"error": "No data provided"}), 400

    new_entry = MyTable(data=data)
    db.session.add(new_entry)
    db.session.commit()
    logger.info(f"Data added with UUID: {new_entry.uuid}")

    return jsonify({
        "message": "Data added successfully",
        "uuid": new_entry.uuid,
        "data": new_entry.data
    })

@app.route('/get-all', methods=['GET'])
def get_all():
    entries = MyTable.query.all()
    logger.info("Fetched all entries from 'mytable'.")
    return jsonify([{
        "uuid": entry.uuid,
        "data": entry.data
    } for entry in entries])

@app.route('/', methods=['GET'])
def health_check():
    logger.info("Root endpoint '/' was accessed.")
    return jsonify({"status": "Flask server is running"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
from flask import Blueprint, jsonify, request
from extensions.database import db


# Routes for Mentor Application Process
@app.route('/submit-mentor-application', methods=['POST'])
def submit_mentor_application():
    try:
        data = request.json

        # Create User
        new_user = User(
            email=data['email'],
            cognito_sub=data.get('cognito_sub')
        )
        db.session.add(new_user)

        # Create Mentor Profile
        new_mentor_profile = MentorProfile(
            user=new_user,
            first_name=data['first_name'],
            last_name=data['last_name'],
            bio=data.get('bio', ''),
            expertise_areas=data.get('expertise_areas', []),
            years_of_experience=data.get('years_of_experience')
        )
        db.session.add(new_mentor_profile)

        db.session.commit()

        logger.info(f"Mentor application submitted for {new_user.email}")
        return jsonify({
            "message": "Mentor application submitted successfully",
            "user_id": new_user.id,
            "mentor_profile_id": new_mentor_profile.id
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error submitting mentor application: {str(e)}")
        return jsonify({"error": str(e)}), 400


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
        db.session.execute(text('SELECT 1'))
        logger.info("Checked database connectivity successfully.")
        return jsonify({"message": "Database 'tct_database' exists and is accessible"})

    except OperationalError as e:
        # possible connection issue (wrong host, credentials, etc.)
        logger.error(f"Could not connect to database: {str(e)}")
        return jsonify({
            "error": "Database connection failed",
            "details": str(e)
        }), 500

    except ProgrammingError as e:
        # check if database does not exit
        logger.warning(f"Database does not exist or is not accessible: {str(e)}")
        return jsonify({
            "error": "Database does not exist",
            "details": str(e)
        }), 404

    except Exception as e:
        # other unexpected exceptions
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": "Unexpected error occurred",
            "details": str(e)
        }), 500


# be able to call
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
    inspector = inspect(db.engine)

    # Check if the table exists
    if 'mytable' not in inspector.get_table_names():
        logger.warning("'mytable' does not exist. Creating all tables.")
        db.create_all()
        logger.info("'mytable' and any other missing tables created.")

    # Query all entries
    entries = MyTable.query.all()
    logger.info("Fetched all entries from 'mytable'.")

    return jsonify([{
        "uuid": entry.uuid,
        "data": entry.data
    } for entry in entries])


@app.route('/', methods=['GET'])
def health_check():
    logger.info("Root endpoint '/' was accessed.")
    return jsonify({"status": "Flask app with PostgreSQL is running"}), 200

    return app
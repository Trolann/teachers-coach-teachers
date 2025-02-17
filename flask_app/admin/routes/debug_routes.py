from flask import Blueprint, jsonify, request
from sqlalchemy.exc import OperationalError, ProgrammingError
from flask_app.models.user import User, MyTable
from flask_app.models.mentor_profiles import MentorProfile
from sqlalchemy import text, inspect
from extensions.database import db
from extensions.cognito import require_auth
from extensions.logging import get_logger

logger = get_logger(__name__)

debug_bps = Blueprint('debug', __name__)

@debug_bps.route('/submit-mentor-application', methods=['POST'])
def submit_mentor_application():
    try:
        data = request.json
        logger.debug(f"Received mentor application data: {data}")

        # Create User
        new_user = User(
            email=data['email'],
            cognito_sub=data.get('cognito_sub')
        )
        logger.debug(f"Creating new user with email: {data['email']}")
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
        logger.info(f"Successfully created mentor profile for user ID: {new_user.id}")
        
        response_data = {
            "message": "Mentor application submitted successfully",
            "user_id": new_user.id,
            "mentor_profile_id": new_mentor_profile.id
        }
        logger.debug(f"Returning response: {response_data}")
        return jsonify(response_data), 201

    except Exception as e:
        logger.error(f"Failed to create mentor application: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@debug_bps.route('/check-database', methods=['GET'])
@require_auth
def check_database():
    logger.info("Checking database connection")
    try:
        db.session.execute(text('SELECT 1'))
        logger.info("Database connection successful")
        return jsonify({"message": "Database 'tct_database' exists and is accessible"})

    except OperationalError as e:
        # possible connection issue (wrong host, credentials, etc.)
        logger.error(f"Database connection failed: {str(e)}")
        return jsonify({
            "error": "Database connection failed",
            "details": str(e)
        }), 500

    except ProgrammingError as e:
        # check if database does not exit
        logger.error(f"Database does not exist: {str(e)}")
        return jsonify({
            "error": "Database does not exist",
            "details": str(e)
        }), 404

    except Exception as e:
        # other unexpected exceptions
        logger.error(f"Unexpected database error: {str(e)}")
        return jsonify({
            "error": "Unexpected error occurred",
            "details": str(e)
        }), 500


# be able to call
@debug_bps.route('/check-table', methods=['GET'])
def check_table():
    logger.info("Checking 'mytable' existence")
    inspector = inspect(db.engine)
    table_names = inspector.get_table_names()
    logger.debug(f"Found tables: {table_names}")
    
    if 'mytable' in table_names:
        logger.info("Table 'mytable' exists")
        return jsonify({"message": "Table 'mytable' exists"})
    else:
        logger.info("Creating 'mytable'")
        db.create_all()
        return jsonify({"message": "Table 'mytable' was created"})


@debug_bps.route('/add-data', methods=['POST'])
def add_data():
    data = request.json.get('data')
    logger.debug(f"Received data: {data}")
    
    if not data:
        logger.warning("No data provided in request")
        return jsonify({"error": "No data provided"}), 400

    try:
        new_entry = MyTable(data=data)
        db.session.add(new_entry)
        db.session.commit()
        logger.info(f"Successfully added new entry with UUID: {new_entry.uuid}")
        
        response = {
            "message": "Data added successfully",
            "uuid": new_entry.uuid,
            "data": new_entry.data
        }
        logger.debug(f"Returning response: {response}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Failed to add data: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Failed to add data"}), 500


@debug_bps.route('/get-all', methods=['GET'])
@require_auth
def get_all():
    logger.info("Fetching all entries from mytable")
    inspector = inspect(db.engine)
    table_names = inspector.get_table_names()
    logger.debug(f"Found tables: {table_names}")

    # Check if the table exists
    if 'mytable' not in table_names:
        logger.info("Table 'mytable' not found, creating it")
        db.create_all()

    try:
        # Query all entries
        entries = MyTable.query.all()
        logger.debug(f"Found {len(entries)} entries")
        
        response = [{
            "uuid": entry.uuid,
            "data": entry.data
        } for entry in entries]
        return jsonify(response)
    except Exception as e:
        logger.error(f"Failed to fetch entries: {str(e)}")
        return jsonify({"error": "Failed to fetch entries"}), 500


@debug_bps.route('/health', methods=['GET'])
def health_check():
    logger.debug("Health check endpoint called")
    return jsonify({"status": "Flask app with PostgreSQL is running"}), 200

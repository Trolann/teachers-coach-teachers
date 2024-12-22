from flask import Blueprint, jsonify, request
from sqlalchemy.exc import OperationalError, ProgrammingError
from flask_app.models.user import User, MentorProfile, MyTable
from sqlalchemy import text, inspect
from extensions.database import db
from extensions.cognito import require_auth

debug_bps = Blueprint('debug', __name__)

@debug_bps.route('/submit-mentor-application', methods=['POST'])
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
        
        response_data = {
            "message": "Mentor application submitted successfully",
            "user_id": new_user.id,
            "mentor_profile_id": new_mentor_profile.id
        }
        return jsonify(response_data), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@debug_bps.route('/check-database', methods=['GET'])
def check_database():
    try:
        db.session.execute(text('SELECT 1'))
        return jsonify({"message": "Database 'tct_database' exists and is accessible"})

    except OperationalError as e:
        # possible connection issue (wrong host, credentials, etc.)
        return jsonify({
            "error": "Database connection failed",
            "details": str(e)
        }), 500

    except ProgrammingError as e:
        # check if database does not exit
        return jsonify({
            "error": "Database does not exist",
            "details": str(e)
        }), 404

    except Exception as e:
        # other unexpected exceptions
        return jsonify({
            "error": "Unexpected error occurred",
            "details": str(e)
        }), 500


# be able to call
@debug_bps.route('/check-table', methods=['GET'])
def check_table():
    inspector = inspect(db.engine)
    table_names = inspector.get_table_names()
    
    if 'mytable' in table_names:
        return jsonify({"message": "Table 'mytable' exists"})
    else:
        db.create_all()
        return jsonify({"message": "Table 'mytable' was created"})


@debug_bps.route('/add-data', methods=['POST'])
def add_data():
    data = request.json.get('data')
    
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        new_entry = MyTable(data=data)
        db.session.add(new_entry)
        db.session.commit()
        
        response = {
            "message": "Data added successfully",
            "uuid": new_entry.uuid,
            "data": new_entry.data
        }
        return jsonify(response)
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to add data"}), 500


@debug_bps.route('/get-all', methods=['GET'])
@require_auth
def get_all():
    inspector = inspect(db.engine)
    table_names = inspector.get_table_names()

    # Check if the table exists
    if 'mytable' not in table_names:
        db.create_all()

    try:
        # Query all entries
        entries = MyTable.query.all()
        
        response = [{
            "uuid": entry.uuid,
            "data": entry.data
        } for entry in entries]
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": "Failed to fetch entries"}), 500


@debug_bps.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Flask app with PostgreSQL is running"}), 200

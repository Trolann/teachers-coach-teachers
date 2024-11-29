from sqlite3 import OperationalError
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from uuid import uuid4
from sqlalchemy.exc import ProgrammingError
from sqlalchemy import inspect, text
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import os


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
# TODO: delete this if it works and figure out how to put in the env
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy and Migrate
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# Mentor Application Status Enum
class MentorStatus(str):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

class User(db.Model):
    """Base User Model"""
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    cognito_sub = db.Column(db.String(100), unique=True, nullable=True)  # AWS Cognito user ID
    
    # Relationships
    mentor_profile = db.relationship('MentorProfile', uselist=False, back_populates='user')
    sessions = db.relationship('MentorshipSession', back_populates='user')

class MentorProfile(db.Model):
    """Detailed Mentor Profile"""
    __tablename__ = 'mentor_profiles'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Mentor-specific fields
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.Text)
    expertise_areas = db.Column(db.ARRAY(db.String), nullable=True)
    years_of_experience = db.Column(db.Integer)
    
    # Application status
    application_status = db.Column(db.String(20), default=MentorStatus.PENDING)
    application_submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Vector embedding for matching
    vector_embedding = db.Column(db.ARRAY(db.Float), nullable=True)
    
    # Relationships
    user = db.relationship('User', back_populates='mentor_profile')
    sessions = db.relationship('MentorshipSession', back_populates='mentor')

class MentorshipSession(db.Model):
    """Mentorship Session Tracking"""
    __tablename__ = 'mentorship_sessions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    
    # Foreign Keys
    mentee_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    mentor_id = db.Column(db.String(36), db.ForeignKey('mentor_profiles.id'), nullable=False)
    
    # Session Details
    scheduled_datetime = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20))  # e.g., scheduled, completed, cancelled
    
    # Integration Details
    zoom_meeting_link = db.Column(db.String(255))
    google_calendar_event_id = db.Column(db.String(100))
    
    # Feedback and Tracking
    mentee_feedback = db.Column(db.Text)
    mentor_feedback = db.Column(db.Text)
    
    # Relationships
    user = db.relationship('User', back_populates='sessions')
    mentor = db.relationship('MentorProfile', back_populates='sessions')

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
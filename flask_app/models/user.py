from uuid import uuid4
from datetime import datetime
from extensions.database import db
from enum import Enum
from extensions.logging import get_logger

logger = get_logger(__name__)

class MentorStatus(Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'



class MyTable(db.Model):
    """Debug-only table, used in debug_routes"""
    __tablename__ = 'mytable'
    __table_args__ = {'extend_existing': True}
    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    data = db.Column(db.String(255))

class User(db.Model):
    """Base User Model"""
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    cognito_sub = db.Column(db.String(100), unique=True, nullable=True)  # AWS Cognito user ID

    # Relationships
    mentor_profile = db.relationship('MentorProfile', uselist=False, back_populates='user')
    sessions = db.relationship('MentorshipSession', back_populates='user')

    def __init__(self, email, cognito_sub=None):
        logger.debug(f"Creating new User with email: {email[:3]}***{email[-4:]}")
        self.email = email
        self.cognito_sub = cognito_sub
        logger.info(f"User created with ID: {self.id}")


class MentorProfile(db.Model):
    """Detailed Mentor Profile"""
    # If this is updated, remember to update the fake_mentors.py script and associated admin panel routes
    __tablename__ = 'mentor_profiles'
    __table_args__ = {'extend_existing': True}

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

    def __init__(self, user_id, first_name, last_name, **kwargs):
        logger.debug(f"Creating new MentorProfile for user_id: {user_id}")
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        for key, value in kwargs.items():
            setattr(self, key, value)
        logger.info(f"MentorProfile created with ID: {self.id}")

    def update_status(self, new_status):
        """Update the application status of a mentor"""
        logger.debug(f"Updating mentor {self.id} status from {self.application_status} to {new_status}")
        self.application_status = new_status
        logger.info(f"Mentor {self.id} status updated to {new_status}")

    # Vector embedding for matching
    vector_embedding = db.Column(db.ARRAY(db.Float), nullable=True)

    # Relationships
    user = db.relationship('User', back_populates='mentor_profile')
    sessions = db.relationship('MentorshipSession', back_populates='mentor')


class MentorshipSession(db.Model):
    """Mentorship Session Tracking"""
    __tablename__ = 'mentorship_sessions'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))

    # Foreign Keys
    mentee_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    mentor_id = db.Column(db.String(36), db.ForeignKey('mentor_profiles.id'), nullable=False)

    # Session Details
    scheduled_datetime = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20))  # e.g., scheduled, completed, cancelled

    def __init__(self, mentee_id, mentor_id, scheduled_datetime, duration_minutes):
        logger.debug(f"Creating new MentorshipSession: mentee={mentee_id}, mentor={mentor_id}")
        self.mentee_id = mentee_id
        self.mentor_id = mentor_id
        self.scheduled_datetime = scheduled_datetime
        self.duration_minutes = duration_minutes
        self.status = 'scheduled'
        logger.info(f"MentorshipSession created with ID: {self.id}")

    def update_status(self, new_status):
        """Update the status of a mentorship session"""
        logger.debug(f"Updating session {self.id} status from {self.status} to {new_status}")
        self.status = new_status
        logger.info(f"Session {self.id} status updated to {new_status}")

    def add_feedback(self, feedback, feedback_type):
        """Add feedback to the session"""
        logger.debug(f"Adding {feedback_type} feedback to session {self.id}")
        if feedback_type == 'mentee':
            self.mentee_feedback = feedback
        elif feedback_type == 'mentor':
            self.mentor_feedback = feedback
        logger.info(f"Added {feedback_type} feedback to session {self.id}")

    # Integration Details
    zoom_meeting_link = db.Column(db.String(255))
    google_calendar_event_id = db.Column(db.String(100))

    # Feedback and Tracking
    mentee_feedback = db.Column(db.Text)
    mentor_feedback = db.Column(db.Text)

    # Relationships
    user = db.relationship('User', back_populates='sessions')
    mentor = db.relationship('MentorProfile', back_populates='sessions')

from uuid import uuid4
from datetime import datetime
from extensions.database import db
from enum import Enum

class MentorStatus(Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'


# TODO: Delete MyTable model (debug only)
# Define the table model
class MyTable(db.Model):
    __tablename__ = 'mytable'
    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    data = db.Column(db.String(255))

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
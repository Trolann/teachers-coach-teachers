from extensions.database import db
from extensions.logging import get_logger
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any

logger = get_logger(__name__)

class UserType(Enum):
    MENTOR = 'mentor'
    MENTEE = 'mentee'
    ADMIN = 'admin'  # This is defined correctly, but the database schema needs to be updated

class ApplicationStatus(Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    REVOKED = 'revoked'

class User(db.Model):
    """User Model with JSON profile storage"""
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    cognito_sub = db.Column(db.String(100), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    user_type = db.Column(db.Enum(UserType), nullable=False, index=True)
    profile = db.Column(db.JSON, nullable=False, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # For users only - stored here for easy querying
    application_status = db.Column(db.Enum(ApplicationStatus), nullable=True, index=True)

    def __init__(self, email: str, user_type: UserType, cognito_sub: str, profile: Optional[Dict[str, Any]] = None, application_status: Optional[ApplicationStatus] = None):
        logger.debug(f"Creating new User with email: {email[:3]}***{email[-4:]}")
        self.cognito_sub = cognito_sub
        self.email = email
        self.user_type = user_type
        self.profile = profile or {}
        self.application_status = application_status
        logger.info(f"User created with ID: {self.cognito_sub}")

    @classmethod
    def get_by_id(cls, cognito_sub: str):
        return cls.query.filter_by(cognito_sub=cognito_sub).first()

    @classmethod
    def get_by_email(cls, email: str):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_mentors(cls, application_status: Optional[str] = None):
        query = cls.query.filter_by(user_type=UserType.MENTOR)
        if application_status:
            query = query.filter_by(application_status=application_status)
        return query.all()

    @classmethod
    def get_mentees(cls):
        return cls.query.filter_by(user_type=UserType.MENTEE).all()

    def update_profile(self, profile_data: Dict[str, Any]):
        """Update profile with new data, merging with existing"""
        self.profile.update(profile_data)
        logger.info(f"Profile updated for user: {self.cognito_sub}")

    def update_application_status(self, status: str):
        """Update mentor application status"""
        if self.user_type != UserType.MENTOR:
            raise ValueError("Cannot update application status for non-mentor users")
        self.application_status = status
        logger.info(f"Mentor application status updated to {status} for user: {self.cognito_sub}")

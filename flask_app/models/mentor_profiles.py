from uuid import uuid4
from datetime import datetime
from extensions.database import db
from enum import Enum
from extensions.logging import get_logger
from sqlalchemy.dialects.postgresql import JSONB

logger = get_logger(__name__)

class MentorStatus(Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    REVOKED = 'revoked'

class MentorProfile(db.Model):
    """Mentor Profile with JSON storage for profile data"""
    __tablename__ = 'mentor_profiles'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Profile data stored as JSON
    profile_data = db.Column(JSONB, nullable=True)
    
    # Application status
    application_status = db.Column(db.String(20), default=MentorStatus.PENDING.value)
    application_submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_id, profile_data=None, **kwargs):
        logger.debug(f"Creating new MentorProfile for user_id: {user_id}")
        self.user_id = user_id
        self.profile_data = profile_data or {}
        for key, value in kwargs.items():
            setattr(self, key, value)
        logger.info(f"MentorProfile created with ID: {self.id}")

    def update_status(self, new_status):
        """Update the application status of a mentor"""
        if not isinstance(new_status, MentorStatus):
            new_status = MentorStatus(new_status)
        logger.debug(f"Updating mentor {self.id} status from {self.application_status} to {new_status.value}")
        self.application_status = new_status.value
        logger.info(f"Mentor {self.id} status updated to {new_status.value}")

from uuid import uuid4
from datetime import datetime
from extensions.database import db
from enum import Enum
from extensions.logging import get_logger
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from flask_app.models.mentorship_session import MentorshipSession

logger = get_logger(__name__)

class MentorStatus(Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    REVOKED = 'revoked'

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

from extensions.database import db
from extensions.logging import get_logger
from enum import Enum
from datetime import datetime
from uuid import uuid4
from typing import Optional, Dict, Any, List

logger = get_logger(__name__)


class SessionStatus(Enum):
    SCHEDULED = 'scheduled'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    RESCHEDULED = 'rescheduled'


class MentorshipSession(db.Model):
    """Mentorship Session Tracking"""
    __tablename__ = 'mentorship_sessions'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))

    # Direct references to users
    mentee_id = db.Column(db.String(100), db.ForeignKey('users.cognito_sub', ondelete='CASCADE'),
                          nullable=False, index=True)
    mentor_id = db.Column(db.String(100), db.ForeignKey('users.cognito_sub', ondelete='CASCADE'),
                          nullable=False, index=True)

    # Session details
    scheduled_datetime = db.Column(db.DateTime, nullable=False, index=True)
    duration_minutes = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(SessionStatus), default=SessionStatus.SCHEDULED, index=True)

    # Feedback and metadata
    mentor_feedback = db.Column(db.JSON, nullable=True)  # From the mentor
    mentee_feedback = db.Column(db.JSON, nullable=True)  # From the mentee
    meta_data = db.Column(db.JSON, nullable=True)  # For any additional data

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, mentee_id: str, mentor_id: str, scheduled_datetime: datetime,
                 duration_minutes: int):
        logger.debug(f"Creating new MentorshipSession: mentee={mentee_id}, mentor={mentor_id}")
        self.mentee_id = mentee_id
        self.mentor_id = mentor_id
        self.scheduled_datetime = scheduled_datetime
        self.duration_minutes = duration_minutes
        self.status = SessionStatus.SCHEDULED
        self.feedback = {}
        self.metadata = {}
        logger.info(f"MentorshipSession created with ID: {self.id}")

    def update_status(self, new_status: SessionStatus):
        """Update session status"""
        logger.debug(f"Updating session {self.id} status from {self.status} to {new_status}")
        self.status = new_status
        logger.info(f"Session {self.id} status updated to {new_status}")

    def add_feedback(self, feedback_data: Dict[str, Any], feedback_type: str):
        """Add feedback from mentor or mentee"""
        if not self.feedback:
            self.feedback = {}
        self.feedback[feedback_type] = feedback_data
        logger.info(f"Added {feedback_type} feedback to session {self.id}")

    def update_metadata(self, metadata: Dict[str, Any]):
        """Update session metadata"""
        if not self.metadata:
            self.metadata = {}
        self.metadata.update(metadata)

    @classmethod
    def get_by_mentee(cls, mentee_id: str, status: Optional[SessionStatus] = None) -> List['MentorshipSession']:
        """Get sessions for a mentee, optionally filtered by status"""
        query = cls.query.filter_by(mentee_id=mentee_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(cls.scheduled_datetime.desc()).all()

    @classmethod
    def get_by_mentor(cls, mentor_id: str, status: Optional[SessionStatus] = None) -> List['MentorshipSession']:
        """Get sessions for a mentor, optionally filtered by status"""
        query = cls.query.filter_by(mentor_id=mentor_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(cls.scheduled_datetime.desc()).all()
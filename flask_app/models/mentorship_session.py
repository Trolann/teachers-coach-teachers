from uuid import uuid4
from extensions.database import db
from extensions.logging import get_logger

logger = get_logger(__name__)

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


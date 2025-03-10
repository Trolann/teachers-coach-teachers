from extensions.database import db
from extensions.logging import get_logger

# Import all models here to register them with SQLAlchemy
from flask_app.models.user import User
from flask_app.models.mentor_profiles import MentorStatus
from flask_app.models.mentorship_session import MentorshipSession
from flask_app.models.credits import CreditRedemption, CreditTransfer

__all__ = [
    'User',
    'MentorStatus',
    'MentorshipSession',
    'CreditRedemption',
    'CreditTransfer'
]

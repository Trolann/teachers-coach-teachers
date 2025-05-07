from extensions.database import db
from extensions.logging import get_logger

# Import all models here to register them with SQLAlchemy
from flask_app.models.user import User, UserType, ApplicationStatus
from flask_app.models.mentorship_session import MentorshipSession
from flask_app.models.credits import CreditRedemption, CreditTransfer
from flask_app.models.embedding import UserEmbedding

__all__ = [
    'User',
    'UserType',
    'UserEmbedding',
    'ApplicationStatus',
    'MentorshipSession',
    'CreditRedemption',
    'CreditTransfer'
]

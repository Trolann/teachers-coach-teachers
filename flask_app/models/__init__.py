from extensions.database import db
from extensions.logging import get_logger

# Import all models here to register them with SQLAlchemy
from .user import User, MyTable
from .mentor_profiles import MentorProfile, MentorStatus
from .mentorship_session import MentorshipSession
from .credits import CreditRedemption, CreditTransfer

__all__ = [
    'User',
    'MyTable', 
    'MentorProfile',
    'MentorStatus',
    'MentorshipSession',
    'CreditRedemption',
    'CreditTransfer'
]

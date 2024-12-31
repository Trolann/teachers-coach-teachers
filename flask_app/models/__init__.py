from models.user import User, MyTable
from models.credits import CreditRedemption, CreditTransfer
from models.mentor_profiles import MentorProfile
from models.mentorship_session import MentorshipSession

# Ensure models are only imported once
__all__ = [
    'User',
    'MentorProfile',
    'MentorshipSession',
    'MyTable',
    'CreditRedemption',
    'CreditTransfer'
]from extensions.database import db
from extensions.logging import get_logger

# Import all models here to register them with SQLAlchemy
from .user import User, MyTable
from .mentor_profiles import MentorProfile, MentorStatus
from .mentorship_session import MentorshipSession

__all__ = [
    'User',
    'MyTable',
    'MentorProfile',
    'MentorStatus',
    'MentorshipSession',
]

from uuid import uuid4
from extensions.database import db
from enum import Enum
from extensions.logging import get_logger
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .mentor_profiles import MentorProfile
    from .mentorship_session import MentorshipSession

logger = get_logger(__name__)

# TODO: Remove MyTable class after debugging
class MyTable(db.Model):
    """Debug-only table, used in debug_routes"""
    __tablename__ = 'mytable'
    __table_args__ = {'extend_existing': True}
    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    data = db.Column(db.String(255))

class User(db.Model):
    """Base User Model"""
    __tablename__ = 'users'
    __table_args__ = (
        db.CheckConstraint('credits >= 0', name='check_positive_credits'),
        {'extend_existing': True}
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    cognito_sub = db.Column(db.String(100), unique=True, nullable=True)  # AWS Cognito user ID
    credits = db.Column(db.Integer, default=0)

    # Relationships
    mentor_profile: Mapped[Optional["MentorProfile"]] = relationship(
        "MentorProfile", uselist=False, backref="user"
    )
    sessions: Mapped[List["MentorshipSession"]] = relationship(
        "MentorshipSession",
        foreign_keys="MentorshipSession.mentee_id",
        backref="user"
    )
    # Credit relationships
    credits_created = db.relationship(
        'flask_app.models.credits.CreditRedemption',
        foreign_keys='CreditRedemption.created_by',
        back_populates='creator'
    )
    credits_redeemed = db.relationship(
        'flask_app.models.credits.CreditRedemption',
        foreign_keys='CreditRedemption.redeemed_by',
        back_populates='redeemer'
    )
    credits_sent = db.relationship(
        'flask_app.models.credits.CreditTransfer',
        foreign_keys='CreditTransfer.from_user_id',
        back_populates='from_user'
    )
    credits_received = db.relationship(
        'flask_app.models.credits.CreditTransfer',
        foreign_keys='CreditTransfer.to_user_id',
        back_populates='to_user'
    )

    def __init__(self, email, cognito_sub=None):
        logger.debug(f"Creating new User with email: {email[:3]}***{email[-4:]}")
        self.email = email
        self.cognito_sub = cognito_sub
        logger.info(f"User created with ID: {self.id}")



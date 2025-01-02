from uuid import uuid4
from extensions.database import db
from enum import Enum
from extensions.logging import get_logger
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .mentor_profiles import MentorProfile
    from .mentorship_session import MentorshipSession

from flask_app.models.credits import CreditRedemption, CreditTransfer

logger = get_logger(__name__)

# TODO: Remove MyTable class after debugging
class MyTable(db.Model):
    """Debug-only table, used in debug_routes"""
    __tablename__ = 'mytable'
    __table_args__ = {'extend_existing': True}
    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    data = db.Column(db.String(255))

class User(db.Model):
    """Base User Model.
    Full paths for relationships are absolutely required and cannot be removed.
    """
    __tablename__ = 'users'
    __table_args__ = (
        db.CheckConstraint('credits >= 0', name='check_positive_credits'),
        {'extend_existing': True}
    )

    id: Mapped[str] = mapped_column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False)
    cognito_sub: Mapped[Optional[str]] = mapped_column(db.String(100), unique=True, nullable=True)
    credits: Mapped[int] = mapped_column(db.Integer, default=0)

    # Relationships - FULL PATHS REQUIRED TO PREVENT MULTIPLE CLASS ERRORS
    credits_created: Mapped[List["flask_app.models.credits.CreditRedemption"]] = relationship(
        "flask_app.models.credits.CreditRedemption",
        back_populates="creator",
        primaryjoin="flask_app.models.user.User.id == foreign(flask_app.models.credits.CreditRedemption.created_by)"
    )

    credits_redeemed: Mapped[List["flask_app.models.credits.CreditRedemption"]] = relationship(
        "flask_app.models.credits.CreditRedemption",
        back_populates="redeemer",
        primaryjoin="flask_app.models.user.User.id == foreign(flask_app.models.credits.CreditRedemption.redeemed_by)"
    )

    credits_sent: Mapped[List["flask_app.models.credits.CreditTransfer"]] = relationship(
        "flask_app.models.credits.CreditTransfer",
        primaryjoin="flask_app.models.user.User.id == foreign(flask_app.models.credits.CreditTransfer.from_user_id)",
        back_populates="from_user"
    )

    credits_received: Mapped[List["flask_app.models.credits.CreditTransfer"]] = relationship(
        "flask_app.models.credits.CreditTransfer",
        primaryjoin="flask_app.models.user.User.id == foreign(flask_app.models.credits.CreditTransfer.to_user_id)",
        back_populates="to_user"
    )


    def __init__(self, email, cognito_sub=None):
        logger.debug(f"Creating new User with email: {email[:3]}***{email[-4:]}")
        self.email = email
        self.cognito_sub = cognito_sub
        logger.info(f"User created with ID: {self.id}")

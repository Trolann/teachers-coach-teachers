from extensions.database import db
from uuid import uuid4
from enum import Enum
import random
from sqlalchemy import and_
from extensions.logging import get_logger
from sqlalchemy.orm import Mapped, relationship, mapped_column
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey


logger = get_logger(__name__)

class TransferType(Enum):
    REDEMPTION = 'redemption'
    MENTORSHIP = 'mentorship'
    PURCHASE = 'purchase'

class CreditRedemption(db.Model):
    """CreditRedemption Model for tracking credit code creation and redemption"""
    __tablename__ = 'credit_redemptions'
    __table_args__ = (
        db.CheckConstraint('amount > 0', name='check_positive_amount'),
        db.Index('ix_unique_active_code', 'code', 'redeemed_by', unique=True,
                 postgresql_where=db.text('redeemed_by IS NULL')),
        {'extend_existing': True}
    )

    id: Mapped[str] = mapped_column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    code: Mapped[str] = mapped_column(db.String(6), nullable=False, index=True)
    created_by: Mapped[str] = mapped_column(
        db.String(36),
        ForeignKey('users.id', ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    amount: Mapped[int] = mapped_column(db.Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime,
        server_default=db.func.now(),
        index=True
    )
    redeemed_by: Mapped[Optional[str]] = mapped_column(
        db.String(36),
        ForeignKey('users.id', ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    redeemed_at: Mapped[Optional[datetime]] = mapped_column(db.DateTime, nullable=True)

    # Relationships - FULL PATHS REQUIRED TO PREVENT MULTIPLE CLASS ERRORS
    creator: Mapped["flask_app.models.user.User"] = relationship(
        "flask_app.models.user.User",
        foreign_keys=[created_by],
        back_populates="credits_created",
        primaryjoin="flask_app.models.credits.CreditRedemption.created_by==flask_app.models.user.User.id"
    )

    redeemer: Mapped[Optional["flask_app.models.user.User"]] = relationship(
        "flask_app.models.user.User",
        foreign_keys=[redeemed_by],
        back_populates="credits_redeemed",
        primaryjoin="flask_app.models.credits.CreditRedemption.redeemed_by==flask_app.models.user.User.id"
    )

    @classmethod
    def generate_unique_code(cls):
        """Generate a unique 6-digit code, trying for complete uniqueness first"""
        # Try 5 times to generate a completely unique code
        for _ in range(5):
            code = ''.join(str(random.randint(0, 9)) for _ in range(6))
            # Check if code exists at all
            exists = cls.query.filter(cls.code == code).first()
            if not exists:
                return code

        # Fall back to generating a code that's unique among unredeemed codes
        while True:
            code = ''.join(str(random.randint(0, 9)) for _ in range(6))
            # Check if code exists and is unredeemed
            exists = cls.query.filter(
                and_(
                    cls.code == code,
                    cls.redeemed_by.is_(None)
                )
            ).first()
            if not exists:
                logger.info("Generated pseudo-unique code after failing to find completely unique code")
                return code

    def __init__(self, created_by, amount):
        self.created_by = created_by
        self.amount = amount
        self.code = self.generate_unique_code()


class CreditTransfer(db.Model):
    """CreditTransfer Model for tracking credit movements between users"""
    __tablename__ = 'credit_transfers'
    __table_args__ = (
        db.CheckConstraint('amount > 0', name='check_positive_amount'),
        {'extend_existing': True}
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    from_user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    to_user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    amount = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), index=True)
    transfer_type = db.Column(db.Enum(TransferType), nullable=False)

    # Relationships - FULL PATHS REQUIRED TO PREVENT MULTIPLE CLASS ERRORS
    from_user = db.relationship(
        'flask_app.models.user.User',
        foreign_keys=[from_user_id],
        back_populates='credits_sent',
        primaryjoin="CreditTransfer.from_user_id==flask_app.models.user.User.id"
    )
    to_user = db.relationship(
        'flask_app.models.user.User',
        foreign_keys=[to_user_id],
        back_populates='credits_received',
        primaryjoin="CreditTransfer.to_user_id==flask_app.models.user.User.id"
    )

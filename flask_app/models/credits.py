from extensions.database import db
from uuid import uuid4
from enum import Enum
import random
from sqlalchemy import and_
from extensions.logging import get_logger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import datetime
from sqlalchemy import ForeignKey

logger = get_logger(__name__)

class TransferType(Enum):
    REDEMPTION = 'redemption'
    MENTORSHIP = 'mentorship'
    PURCHASE = 'purchase'
    POOL_TRANSFER = 'pool_transfer'

class CreditPool(db.Model):
    """CreditPool Model for managing groups of credits"""
    __tablename__ = 'credit_pools'
    __table_args__ = (
        db.Index('ix_unique_pool_code', 'pool_code', unique=True),
        {'extend_existing': True}
    )

    id: Mapped[str] = mapped_column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    owner_id: Mapped[str] = mapped_column(
        db.String(36),
        ForeignKey('users.id', ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    pool_code: Mapped[str] = mapped_column(db.String(6), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime,
        server_default=db.func.now(),
        index=True
    )
    is_active: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=True)
    credits_available: Mapped[int] = mapped_column(db.Integer, nullable=False, default=0)

    
    @classmethod
    def generate_unique_code(cls):
        """Generate a unique 6-digit code for the pool"""
        while True:
            code = ''.join(str(random.randint(0, 9)) for _ in range(6))
            exists = cls.query.filter(cls.pool_code == code).first()
            if not exists:
                return code

    def __init__(self, owner_id: str, name: str, is_active: bool = True, credits_available: int = 0):
        self.owner_id = owner_id
        self.name = name
        self.pool_code = self.generate_unique_code()
        self.is_active = is_active
        self.credits_available = credits_available

class CreditPoolAccess(db.Model):
    """Model for managing access to credit pools"""
    __tablename__ = 'credit_pool_access'
    __table_args__ = (
        db.UniqueConstraint('pool_id', 'user_email', name='unique_pool_user_access'),
        {'extend_existing': True}
    )

    id: Mapped[str] = mapped_column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    pool_id: Mapped[str] = mapped_column(
        db.String(36),
        ForeignKey('credit_pools.id', ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_email: Mapped[str] = mapped_column(db.String(255), nullable=False, index=True)
    granted_at: Mapped[datetime] = mapped_column(
        db.DateTime,
        server_default=db.func.now()
    )


class CreditRedemption(db.Model):
    """CreditRedemption Model for tracking credit code creation and redemption"""
    __tablename__ = 'credit_redemptions'
    __table_args__ = (
        db.CheckConstraint('amount > 0', name='check_positive_amount'),
        db.Index('ix_unique_active_code', 'code', 'credit_pool_id', unique=True,
                 postgresql_where=db.text('credit_pool_id IS NULL')),
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
    credit_pool_id: Mapped[Optional[str]] = mapped_column(
        db.String(36),
        ForeignKey('credit_pools.id', ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    redeemed_at: Mapped[Optional[datetime]] = mapped_column(db.DateTime, nullable=True)
    redeemed_by_email: Mapped[Optional[str]] = mapped_column(db.String(255), nullable=True)


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
    """CreditTransfer Model for tracking credit movements between pools"""
    __tablename__ = 'credit_transfers'
    __table_args__ = (
        db.CheckConstraint('amount > 0', name='check_positive_amount'),
        {'extend_existing': True}
    )

    id: Mapped[str] = mapped_column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    from_pool_id: Mapped[str] = mapped_column(
        db.String(36),
        ForeignKey('credit_pools.id'),
        nullable=False,
        index=True
    )
    to_pool_id: Mapped[str] = mapped_column(
        db.String(36),
        ForeignKey('credit_pools.id'),
        nullable=False,
        index=True
    )
    initiated_by_email: Mapped[str] = mapped_column(db.String(255), nullable=False)
    amount: Mapped[int] = mapped_column(db.Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, server_default=db.func.now(), index=True)
    transfer_type: Mapped[TransferType] = mapped_column(db.Enum(TransferType), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(db.String(500), nullable=True)

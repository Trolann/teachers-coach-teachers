from extensions.database import db
from uuid import uuid4
from enum import Enum
from extensions.logging import get_logger

logger = get_logger(__name__)

class TransferType(Enum):
    REDEMPTION = 'redemption'
    MENTORSHIP = 'mentorship'
    PURCHASE = 'purchase'

class CreditRedemption(db.Model):
    """CreditRedemption Model for tracking credit code creation and redemption"""
    __tablename__ = 'credit_redemptions'
    __table_args__ = (
        {'extend_existing': True},
        db.CheckConstraint('amount > 0', name='check_positive_amount'),
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    amount = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), index=True)
    redeemed_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True, index=True)
    redeemed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by], back_populates='credits_created')
    redeemer = db.relationship('User', foreign_keys=[redeemed_by], back_populates='credits_redeemed')

    def __init__(self, created_by, amount):
        self.created_by = created_by
        self.amount = amount


class CreditTransfer(db.Model):
    """CreditTransfer Model for tracking credit movements between users"""
    __tablename__ = 'credit_transfers'
    __table_args__ = (
        {'extend_existing': True},
        db.CheckConstraint('amount > 0', name='check_positive_amount'),
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    from_user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    to_user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    amount = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), index=True)
    transfer_type = db.Column(db.Enum(TransferType), nullable=False)

    # Relationships
    from_user = db.relationship('User', foreign_keys=[from_user_id], back_populates='credits_sent')
    to_user = db.relationship('User', foreign_keys=[to_user_id], back_populates='credits_received')
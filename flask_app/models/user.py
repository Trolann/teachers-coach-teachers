from uuid import uuid4
from extensions.database import db
from extensions.logging import get_logger
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column

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

    id: Mapped[str] = mapped_column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False)
    cognito_sub: Mapped[Optional[str]] = mapped_column(db.String(100), unique=True, nullable=True)
    credits: Mapped[int] = mapped_column(db.Integer, default=0)

    def __init__(self, email, cognito_sub=None):
        logger.debug(f"Creating new User with email: {email[:3]}***{email[-4:]}")
        self.email = email
        self.cognito_sub = cognito_sub
        if cognito_sub:
            self.id = cognito_sub
        logger.info(f"User created with ID: {self.id}")

from uuid import uuid4
from extensions.database import db
from extensions.logging import get_logger
from typing import Optional, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import select
from flask_app.models.credits import CreditPool

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
    __table_args__ = {'extend_existing': True}

    id: Mapped[str] = mapped_column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False)
    cognito_sub: Mapped[Optional[str]] = mapped_column(db.String(100), unique=True, nullable=True)

    # Relationships
    owned_pools = relationship("CreditPool", 
                             primaryjoin="User.id==CreditPool.owner_id",
                             backref="owner",
                             cascade="all, delete-orphan")

    def __init__(self, email, cognito_sub=None):
        logger.debug(f"Creating new User with email: {email[:3]}***{email[-4:]}")
        self.email = email
        self.cognito_sub = cognito_sub
        if cognito_sub:
            self.id = cognito_sub
        logger.info(f"User created with ID: {self.id}")

    def create_credit_pool(self, name: str) -> "CreditPool":
        """Create a new credit pool owned by this user"""
        from .credits import CreditPool
        pool = CreditPool(owner_id=self.id, name=name)
        self.owned_pools.append(pool)
        return pool

    def get_accessible_pools(self) -> List["CreditPool"]:
        """Get all credit pools this user has access to (owned + granted access)"""
        from .credits import CreditPool, CreditPoolAccess
        # Get pools user owns
        owned_pools = set(self.owned_pools)
        
        # Get pools user has been granted access to
        access_grants = CreditPoolAccess.query.filter_by(user_email=self.email).all()
        accessible_pools = set(grant.pool for grant in access_grants)
        
        return list(owned_pools | accessible_pools)

    def has_pool_access(self, pool_id: str) -> bool:
        """Check if user has access to a specific pool"""
        from .credits import CreditPool, CreditPoolAccess
        
        # Check if user owns the pool
        if any(pool.id == pool_id for pool in self.owned_pools):
            return True
            
        # Check if user has been granted access
        access = CreditPoolAccess.query.filter_by(
            pool_id=pool_id,
            user_email=self.email
        ).first()
        
        return access is not None

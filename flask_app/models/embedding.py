from extensions.database import db
from extensions.logging import get_logger
from datetime import datetime
from uuid import uuid4
from typing import List, Optional

logger = get_logger(__name__)


class UserEmbedding(db.Model):
    """Vector embeddings for user matching"""
    __tablename__ = 'user_embeddings'
    __table_args__ = (
        db.Index('ix_user_embedding_type', 'user_id', 'embedding_type'),
        {'extend_existing': True}
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String(100), db.ForeignKey('users.cognito_sub', ondelete='CASCADE'),
                        nullable=False, index=True)
    embedding_type = db.Column(db.String(50), nullable=False)
    vector_embedding = db.Column(db.ARRAY(db.Float(precision=8)), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_id: str, embedding_type: str, vector_embedding: List[float]):
        """
        Initialize a new embedding

        Args:
            user_id: User's cognito_sub
            embedding_type: Type of embedding (e.g., 'bio', 'expertise', 'goals')
            vector_embedding: 1536-dimensional vector as a list of floats
        """
        self.user_id = user_id
        self.embedding_type = embedding_type
        self.vector_embedding = vector_embedding
        logger.info(f"Created {embedding_type} embedding for user {user_id}")

    @classmethod
    def get_embedding(cls, user_id: str, embedding_type: str) -> Optional['UserEmbedding']:
        """Get a specific embedding for a user"""
        return cls.query.filter_by(user_id=user_id, embedding_type=embedding_type).first()

    @classmethod
    def get_all_embeddings(cls, user_id: str) -> List['UserEmbedding']:
        """Get all embeddings for a user"""
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def create_or_update(cls, user_id: str, embedding_type: str, vector_embedding: List[float]) -> 'UserEmbedding':
        """Create a new embedding or update if it exists"""
        embedding = cls.get_embedding(user_id, embedding_type)
        if embedding:
            embedding.vector_embedding = vector_embedding
            logger.info(f"Updated {embedding_type} embedding for user {user_id}")
        else:
            embedding = cls(user_id, embedding_type, vector_embedding)
            db.session.add(embedding)
        return embedding
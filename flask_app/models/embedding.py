from extensions.database import db
from extensions.logging import get_logger
from datetime import datetime
from uuid import uuid4
from typing import List
from pgvector.sqlalchemy import Vector

logger = get_logger(__name__)

class UserEmbedding(db.Model):
    """Vector embeddings for user matching using pgvector"""
    __tablename__ = 'user_embeddings'
    __table_args__ = (
        db.Index('ix_user_embedding_type', 'user_id', 'embedding_type'),
        {'extend_existing': True}
    )
    N_DIMENSIONS = 1536  # Number of dimensions for the vector embedding

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String(100), db.ForeignKey('users.cognito_sub', ondelete='CASCADE'),
                        nullable=False, index=True)
    embedding_type = db.Column(db.String(50), nullable=False)
    vector_embedding = db.Column(Vector(N_DIMENSIONS), nullable=False)
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
        logger.debug(f"Created {embedding_type} embedding for user {user_id}")



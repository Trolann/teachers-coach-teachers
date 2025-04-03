from extensions.database import db
from extensions.logging import get_logger
from datetime import datetime
from uuid import uuid4
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import func, text
import numpy as np

logger = get_logger(__name__)

# Register the vector type with SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.types import TypeDecorator, Float

class Vector(TypeDecorator):
    """PostgreSQL vector type for storing embeddings"""
    impl = ARRAY(Float(precision=8))
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return value
        return None


class UserEmbedding(db.Model):
    """Vector embeddings for user matching using pgvector"""
    __tablename__ = 'user_embeddings'
    __table_args__ = (
        db.Index('ix_user_embedding_type', 'user_id', 'embedding_type'),
        {'extend_existing': True}
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String(100), db.ForeignKey('users.cognito_sub', ondelete='CASCADE'),
                        nullable=False, index=True)
    embedding_type = db.Column(db.String(50), nullable=False)
    vector_embedding = db.Column(Vector, nullable=False)
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
    def find_similar_embeddings(cls, 
                               vector_embedding: List[float], 
                               embedding_type: str, 
                               limit: int = 10, 
                               threshold: float = 0.7) -> List[Tuple[str, float]]:
        """
        Find similar embeddings using cosine similarity
        
        Args:
            vector_embedding: The query vector to compare against
            embedding_type: Type of embedding to search
            limit: Maximum number of results to return
            threshold: Minimum similarity score (0-1)
            
        Returns:
            List of tuples containing (user_id, similarity_score)
        """
        # Convert the embedding to a PostgreSQL vector
        embedding_array = np.array(vector_embedding, dtype=np.float32)
        
        # Use raw SQL for the cosine similarity calculation
        # This uses the pgvector extension's <=> operator (cosine distance)
        # We convert to similarity by doing 1 - distance
        query = text("""
            SELECT user_id, 1 - (vector_embedding <=> :embedding) AS similarity
            FROM user_embeddings
            WHERE embedding_type = :embedding_type
            AND 1 - (vector_embedding <=> :embedding) >= :threshold
            ORDER BY similarity DESC
            LIMIT :limit
        """)
        
        result = db.session.execute(
            query,
            {
                "embedding": embedding_array,
                "embedding_type": embedding_type,
                "threshold": threshold,
                "limit": limit
            }
        )
        
        # Return list of (user_id, similarity_score) tuples
        return [(row.user_id, float(row.similarity)) for row in result]

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
        
    @classmethod
    def create_vector_extension(cls) -> None:
        """
        Create the pgvector extension if it doesn't exist
        This should be called during database initialization
        """
        try:
            db.session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            db.session.commit()
            logger.info("pgvector extension created or already exists")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create pgvector extension: {e}")
            raise

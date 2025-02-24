from uuid import uuid4
from datetime import datetime
from extensions.database import db
from pgvector.sqlalchemy import Vector

class MentorVector(db.Model):
    """Vector representation of mentor profiles for similarity search"""
    __tablename__ = 'mentor_vectors'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String(36), nullable=False)
    
    # Vector embedding for similarity search (1536 dimensions for OpenAI embeddings)
    embedding = db.Column(Vector(1536))
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    __table_args__ = (
        db.Index('idx_mentor_vectors_embedding', 'embedding', postgresql_using='ivfflat'),
    )

    def __init__(self, user_id, embedding):
        self.user_id = user_id
        self.embedding = embedding

"""
Migration script to set up pgvector extension and convert existing embeddings
Run this after installing the pgvector extension on your PostgreSQL database
"""

from flask import current_app
from extensions.database import db
from models.embedding import UserEmbedding
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

def setup_pgvector():
    """Set up pgvector extension and create necessary indexes"""
    try:
        # Create the extension
        db.session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        
        # Create index for cosine similarity searches
        # This assumes the table structure has been updated to use the vector type
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS user_embeddings_vector_idx 
            ON user_embeddings 
            USING ivfflat (vector_embedding vector_cosine_ops)
            WITH (lists = 100)
        """))
        
        db.session.commit()
        logger.info("pgvector extension and indexes created successfully")
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to set up pgvector: {e}")
        return False

def run_migration():
    """Run the full migration process"""
    with current_app.app_context():
        # Set up pgvector extension
        if not setup_pgvector():
            logger.error("Failed to set up pgvector extension, aborting migration")
            return False
        
        # The table structure changes should be handled by Alembic migrations
        # This script just ensures the extension is installed
        
        logger.info("pgvector migration completed successfully")
        return True

if __name__ == "__main__":
    # This allows running the migration directly
    from flask import Flask
    from extensions.database import db as _db
    
    app = Flask(__name__)
    app.config.from_object('config.FlaskConfig')
    _db.init_app(app)
    
    with app.app_context():
        run_migration()

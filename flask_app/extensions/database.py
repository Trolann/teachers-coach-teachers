from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from extensions.logging import get_logger

logger = get_logger(__name__)

# Initialize SQLAlchemy with no settings
db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Initialize the database with the app"""
    logger.info("Initializing database connection")
    logger.debug(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', '').split('@')[0]}@****")
    
    try:
        db.init_app(app)
        migrate.init_app(app, db)
        import models
        with app.app_context():
            db.create_all()
        app.db = db  # Make db available as app attribute
        logger.info("Database initialization successful")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        logger.exception(e)
        raise

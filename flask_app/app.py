from flask import Flask
from admin.routes import create_admin_blueprint
from config import FlaskConfig
from secrets import token_hex
from extensions.database import init_db
from extensions.logging import get_logger

logger = get_logger(__name__)

def create_app(config_class=FlaskConfig()):
    """Create and configure Flask application instance"""
    logger.debug(f'Creating Flask app with config: {config_class.__class__.__name__}')
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Set a secure secret key for sessions
    app.secret_key = token_hex(32)
    logger.debug('Generated secure secret key for sessions')

    try:
        # Initialize extensions
        logger.info('Initializing database connection')
        init_db(app)
    except Exception as e:
        logger.error(f'Failed to initialize database: {str(e)}')
        logger.exception(e)
        raise

    # Register blueprints
    logger.info('Registering admin blueprint at /admin')
    app.register_blueprint(create_admin_blueprint(), url_prefix='/admin')

    logger.info('Flask application successfully created')
    return app

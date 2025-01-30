from flask import Flask
from admin.routes import create_admin_blueprint
from api import create_api_blueprint
from config import FlaskConfig
from secrets import token_hex
from extensions.database import init_db
from extensions.logging import get_logger

logger = get_logger(__name__)

def create_app(config_class=FlaskConfig()):
    """Create and configure Flask application instance"""
    logger.info('Starting Flask application creation process')
    logger.debug(f'Initializing with config class: {config_class.__class__.__name__}')
    
    # Initialize Flask app
    logger.info('Creating Flask application instance')
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Log configuration details at debug level
    logger.debug(f'Application configuration loaded - DEBUG={app.config.get("DEBUG")}, '
                f'ENV={app.config.get("ENV")}, '
                f'TESTING={app.config.get("TESTING")}')
    
    # Set a secure secret key for sessions
    app.secret_key = token_hex(32)
    logger.info('Secure session management configured')
    logger.debug('Secret key generated and set for session encryption')

    try:
        # Initialize database connection
        logger.info('Initializing database connection')
        logger.debug(f'Database URI: {app.config.get("SQLALCHEMY_DATABASE_URI", "").split("@")[-1]}')  # Log only host/db part
        init_db(app)
        logger.info('Database connection successfully established and configured')
    except Exception as e:
        logger.error(f'Critical error during database initialization: {str(e)}')
        logger.error('Application startup failed - database connection error')
        logger.exception(e)
        raise

    try:
        # Register blueprints
        logger.info('Registering application blueprints')
        admin_bp = create_admin_blueprint()
        api_bp = create_api_blueprint()
        app.register_blueprint(admin_bp, url_prefix='/admin')
        logger.info('Admin blueprint successfully registered at /admin endpoint')
        logger.debug('Available admin routes will be prefixed with /admin')
        app.register_blueprint(api_bp, url_prefix='/api')
        logger.info('API blueprint successfully registered at /api endpoint')
        logger.debug('Available API routes will be prefixed with /api')
    except Exception as e:
        logger.error(f'Critical error during blueprint registration: {str(e)}')
        logger.error('Application startup failed - blueprint registration error')
        logger.exception(e)
        raise

    logger.info('Flask application successfully created and configured')
    logger.debug('Application instance ready to handle requests')
    return app

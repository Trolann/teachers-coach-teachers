from extensions.logging import get_logger
from flask import Blueprint

logger = get_logger(__name__)

def create_api_blueprint():
    """Creates and configures the admin blueprint with all routes"""
    logger.info('Initializing API blueprint')
    try:
        api_bp = Blueprint('api', __name__)
        logger.debug('Created base API Blueprint instance')

        # Register credit routes
        from .credits.routes import credits_bp
        api_bp.register_blueprint(credits_bp, url_prefix='/credits')

        from .users.routes import user_bp
        api_bp.register_blueprint(user_bp, url_prefix='/users')

        return api_bp

    except Exception as e:
        logger.error(f'Failed to create API blueprint: {str(e)}')
        logger.exception(e)
        raise

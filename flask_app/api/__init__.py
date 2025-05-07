from extensions.logging import get_logger
from flask import Blueprint

logger = get_logger(__name__)

def create_api_blueprint():
    """Creates and configures the admin blueprint with all routes"""
    logger.info('Initializing API blueprint')
    try:
        api_bp = Blueprint('api', __name__)
        logger.debug('Created base API Blueprint instance')

        from .credits.routes import credits_bp
        api_bp.register_blueprint(credits_bp, url_prefix='/credits')

        from .users.picture_routes import picture_bp
        api_bp.register_blueprint(picture_bp, url_prefix='/pictures')

        from .users.routes import user_bp
        api_bp.register_blueprint(user_bp, url_prefix='/users')

        from .users.mentor_status_routes import mentor_status_bp
        api_bp.register_blueprint(mentor_status_bp, url_prefix='/mentor_status')

        from .matching.routes import matching_bp
        api_bp.register_blueprint(matching_bp, url_prefix='/matching')

        # Register sessions routes
        from .sessions.routes import sessions_bp
        api_bp.register_blueprint(sessions_bp, url_prefix='/sessions')

        return api_bp

    except Exception as e:
        logger.error(f'Failed to create API blueprint: {str(e)}')
        logger.exception(e)
        raise

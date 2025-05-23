from extensions.logging import get_logger
from flask import Blueprint

logger = get_logger(__name__)

def create_admin_blueprint():
    """Creates and configures the admin blueprint with all routes"""
    logger.info('Initializing admin blueprint')
    try:
        admin_bp = Blueprint('admin', __name__)
        logger.debug('Created base admin Blueprint instance')

        # Register debug routes
        from .debug_routes import debug_bps
        admin_bp.register_blueprint(debug_bps, url_prefix='/debug')
        logger.info('Registered debug routes at /debug prefix')

        # Register dashboard routes
        from .dashboard import admin_dashboard_bp
        admin_bp.register_blueprint(admin_dashboard_bp, url_prefix='')
        logger.info('Registered dashboard routes at root prefix')

        # Register fake users routes
        from .fake_mentors import fake_mentors_bp
        admin_bp.register_blueprint(fake_mentors_bp, url_prefix='')
        logger.info('Registered fake users routes at root prefix')

        # Register test matching routes
        from .test_matching import test_matching_bp
        admin_bp.register_blueprint(test_matching_bp, url_prefix='')
        logger.info('Registered test matching routes at root prefix')

        # Register credits routes
        from .credits import admin_credits_bp
        admin_bp.register_blueprint(admin_credits_bp, url_prefix='/credits')
        logger.info('Regposistered credits routes at /credits prefix')

        # Register logs routes
        from .logs import logs_bp
        admin_bp.register_blueprint(logs_bp, url_prefix='/logs')
        logger.info('Registered logs routes at /logs prefix')

        logger.info('Successfully created and configured admin blueprint')
        return admin_bp
    except Exception as e:
        logger.error(f'Failed to create admin blueprint: {str(e)}')
        logger.exception(e)
        raise

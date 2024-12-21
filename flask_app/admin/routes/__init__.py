def create_admin_blueprint():
    from flask import Blueprint
    admin_bp = Blueprint('admin', __name__)

    # Register debug routes
    from .debug_routes import debug_bps
    admin_bp.register_blueprint(debug_bps, url_prefix='/debug')

    # Register dashboard routes
    from .dashboard import admin_dashboard_bp
    admin_bp.register_blueprint(admin_dashboard_bp, url_prefix='')

    # Register fake mentors routes
    from .fake_mentors import fake_mentors_bp
    admin_bp.register_blueprint(fake_mentors_bp, url_prefix='')

    return admin_bp



def create_admin_blueprint():
    from flask import Blueprint

    admin_bp = Blueprint('admin', __name__)

    from .debug_routes import debug_bps
    admin_bp.register_blueprint(debug_bps, url_prefix='/debug')

    return admin_bp
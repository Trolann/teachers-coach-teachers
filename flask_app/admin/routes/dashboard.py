from flask import render_template, current_app, Blueprint
from extensions.cognito import require_auth
from sqlalchemy import text

admin_dashboard_bp = Blueprint('admin_dashboard', __name__)


@admin_dashboard_bp.route('/')
def index():
    return render_template('dashboard/login.html')


@admin_dashboard_bp.route('/dashboard')
@require_auth
def dashboard():
    try:
        # Test database connection
        current_app.db.session.execute(text('SELECT 1'))
        db_status = "Successfully connected to database"
    except Exception as e:
        db_status = f"Database connection failed: {str(e)}"

    return render_template('dashboard/index.html', db_status=db_status)
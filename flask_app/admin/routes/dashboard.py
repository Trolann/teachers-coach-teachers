from flask import render_template, current_app, Blueprint, request, redirect, url_for, flash, session
from extensions.database import db
from flask_app.models.user import User, UserType, ApplicationStatus
from extensions.cognito import require_auth, CognitoTokenVerifier
from extensions.logging import get_logger
from sqlalchemy import text
from os import path

logger = get_logger(__name__)

# Get the current directory path
current_dir = path.dirname(path.abspath(__file__))
template_dir = path.join(current_dir, '..', 'templates')
static_dir = path.join(current_dir, '..', 'static')

# Create blueprint with template folder specified
admin_dashboard_bp = Blueprint('admin_dashboard', __name__,
                               static_folder=static_dir,
                               static_url_path='/admin/static',
                               template_folder=template_dir)


@admin_dashboard_bp.route('/', methods=['GET', 'POST'])
def index():
    logger.debug('Rendering admin login page')
    username = request.form.get('username')
    password = request.form.get('password')
    if request.method == 'POST':
        logger.debug(f'Login attempt for user {username}')
        if not username or not password:
            flash('Username and password are required')
            logger.warning(f'Login attempt failed {username}: username or password missing')
            return render_template('dashboard/login.html')

        cognito = CognitoTokenVerifier()
        try:
            logger.info(f'Attempting to login as admin user {username}')
            response = cognito.login_as_admin(username, password)
            if 'error' in response:
                logger.warning(f'Login attempt failed for user {username}: {response["error"]}')
                flash(f'Login failed: {response["error"]}')
                return render_template('dashboard/login.html')

            # Store user information in session
            session['access_token'] = response['AccessToken']
            session['user_id'] = response['user_info']['user_id']  # Cognito sub id
            logger.info(f'Admin user {username} successfully logged into dashboard with ID {session["user_id"]}')
            return redirect(url_for('admin.admin_dashboard.dashboard'))
        except Exception as e:
            flash(f'Login error: {str(e)}')
            logger.error(f'Error logging in as admin user {username}: {str(e)}')
            logger.exception(e)
            return render_template('dashboard/login.html')

    if request.method == 'GET' and 'access_token' in session:
        logger.debug(f'{username} already logged in, redirecting to dashboard')
        return redirect(url_for('admin.admin_dashboard.dashboard'))

    return render_template('dashboard/login.html')


@admin_dashboard_bp.route('/logout')
@require_auth
def logout():
    session.clear()
    logger.debug(f'{session.get("username")} logged out')
    return redirect(url_for('admin.index'))


@admin_dashboard_bp.route('/dashboard')
@require_auth
def dashboard():
    if 'access_token' not in session:
        logger.debug('Routing user to dashboard login page')
        return redirect(url_for('admin.admin_dashboard.index'))
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        db_status = "Successfully connected to database"
        logger.debug('Successfully connected to database')
    except Exception as e:
        logger.error(f'Database connection failed: {str(e)}')
        logger.exception(e)
        db_status = f"Database connection failed: {str(e)}"

    session["username"] = db.session.query(User).filter(User.cognito_sub == session['user_id']).first().email
    logger.info(f'Rendering admin dashboard for {session.get("username")}')
    return render_template('dashboard/index.html', db_status=db_status)

@admin_dashboard_bp.route('/mentors')
#@require_auth
def mentors():
    if 'access_token' not in session:
        logger.debug('Routing user to dashboard login page')
        return redirect(url_for('admin.admin_dashboard.index'))
    mentors = db.session.query(User).filter(User.user_type == UserType.MENTOR).all()
    logger.info(f'Rendering users dashboard for {session.get("username")}')
    return render_template('dashboard/mentors.html', mentors=mentors)

@admin_dashboard_bp.route('/users/status', methods=['POST'])
@require_auth
def update_user_status():
    if 'access_token' not in session:
        logger.warning(f'Unauthorized access to update user status by {request.remote_addr}')
        return {'success': False, 'error': 'Unauthorized'}, 401
    
    try:
        data = request.json
        if not data or 'user_id' not in data or 'status' not in data:
            logger.warning('Invalid request data for user status update')
            return {'success': False, 'error': 'Invalid request data'}, 400
            
        user_id = data['user_id']
        status = data['status']
        
        valid_statuses = ["PENDING", "APPROVED", "REJECTED", "REVOKED"]
        if status not in valid_statuses:
            logger.warning(f'Invalid status {status} requested')
            return {'success': False, 'error': 'Invalid status'}, 400
            
        user = db.session.query(User).filter(User.cognito_sub == user_id).first()
        if not user:
            logger.warning(f'User {user_id} not found')
            return {'success': False, 'error': 'User not found'}, 404
            
        user.application_status = status
        logger.info(f'Updating user {user_id} status to {status} by {session.get("username")}')
        db.session.commit()
        logger.info(f'User {user_id} status updated successfully to {status}')
        return {'success': True}
    except Exception as e:
        logger.error(f'Error updating mentor status: {str(e)}')
        logger.exception(e)
        db.session.rollback()
        return {'success': False, 'error': str(e)}, 500

@admin_dashboard_bp.route('/users/<string:user_id>/approve', methods=['POST'])
@require_auth
def approve_user(user_id):
    """Approve a user application"""
    if 'access_token' not in session:
        logger.warning(f'Unauthorized access to approve user {user_id} by {request.remote_addr}')
        return {'success': False, 'error': 'Unauthorized'}, 401
    
    try:
        user = db.session.query(User).filter(User.cognito_sub == user_id).first()
        if not user:
            logger.warning(f'User {user_id} not found')
            return {'success': False, 'error': 'User not found'}, 404
            
        user.application_status = "APPROVED"
        logger.info(f'Approving user {user_id} by {session.get("username")}')
        db.session.commit()
        logger.info(f'User {user_id} approved successfully')
        return {'success': True}
    except Exception as e:
        logger.error(f'Error approving user {user_id}: {str(e)}')
        logger.exception(e)
        db.session.rollback()
        return {'success': False, 'error': str(e)}, 500

@admin_dashboard_bp.route('/users/<string:user_id>/reject', methods=['POST'])
@require_auth
def reject_user(user_id):
    if 'access_token' not in session:
        logger.warning(f'Unauthorized access to reject user {user_id} by {request.remote_addr}')
        return {'success': False, 'error': 'Unauthorized'}, 401
    
    try:
        user = db.session.query(User).filter(User.cognito_sub == user_id).first()
        if not user:
            logger.warning(f'User {user_id} not found')
            return {'success': False, 'error': 'User not found'}, 404
            
        user.application_status = "REJECTED"
        logger.info(f'Rejecting user {user_id} by {session.get("username")}')
        db.session.commit()
        logger.info(f'User {user_id} rejected successfully')
        return {'success': True}
    except Exception as e:
        logger.error(f'Error rejecting user {user_id}: {str(e)}')
        logger.exception(e)
        db.session.rollback()
        return {'success': False, 'error': str(e)}, 500

@admin_dashboard_bp.route('/users/<string:user_id>/revoke', methods=['POST'])
@require_auth
def revoke_user(user_id):
    if 'access_token' not in session:
        logger.warning(f'Unauthorized access to revoke user {user_id} by {request.remote_addr}')
        return {'success': False, 'error': 'Unauthorized'}, 401
    
    try:
        user = db.session.query(User).filter(User.cognito_sub == user_id).first()
        if not user:
            logger.warning(f'User {user_id} not found')
            return {'success': False, 'error': 'User not found'}, 404
            
        user.application_status = "REVOKED"
        logger.info(f'Revoking user {user_id} by {session.get("username")}')
        db.session.commit()
        logger.info(f'User {user_id} approval revoked successfully')
        return {'success': True}
    except Exception as e:
        logger.error(f'Error revoking user {user_id}: {str(e)}')
        logger.exception(e)
        db.session.rollback()
        return {'success': False, 'error': str(e)}, 500

from flask import render_template, current_app, Blueprint, request, redirect, url_for, flash, session
from extensions.database import db
from flask_app.models.user import MentorProfile
from extensions.cognito import require_auth, CognitoBackendAuthorizer
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

        cognito = CognitoBackendAuthorizer()
        try:
            logger.info(f'Attempting to login as admin user {username}')
            response = cognito.login_as_admin(username, password)
            if 'error' in response:
                logger.warning(f'Login attempt failed for user {username}: {response["error"]}')
                flash(f'Login failed: {response["error"]}')
                return render_template('dashboard/login.html')

            # Store the access token
            session['access_token'] = response['AccessToken']
            logger.info(f'Admin user {username} successfully logged into dashboard')
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
def logout():
    session.clear()
    logger.debug(f'{session.get("username")} logged out')
    return redirect(url_for('admin.index'))


@admin_dashboard_bp.route('/dashboard')
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

    logger.info(f'Rendering admin dashboard for {session.get("username")}')
    return render_template('dashboard/index.html', db_status=db_status)

@admin_dashboard_bp.route('/mentors')
def mentors():
    if 'access_token' not in session:
        logger.debug('Routing user to dashboard login page')
        return redirect(url_for('admin.admin_dashboard.index'))
    mentors = db.session.query(MentorProfile).all()
    logger.info(f'Rendering mentors dashboard for {session.get("username")}')
    return render_template('dashboard/mentors.html', mentors=mentors)

@admin_dashboard_bp.route('/mentors/<int:mentor_id>/approve', methods=['POST'])
def approve_mentor(mentor_id):
    if 'access_token' not in session:
        # Show IP address in logs
        logger.warn(f'Unauthorized access to approve mentor {mentor_id} by {request.remote_addr}')
        return {'success': False, 'error': 'Unauthorized'}, 401
    
    try:
        mentor = db.session.query(MentorProfile).filter(MentorProfile.id == str(mentor_id)).first()
        if not mentor:
            return {'success': False, 'error': 'Mentor not found'}, 404
        logger.info(f'Approving mentor {mentor_id} for {session.get("username")}')
        mentor.application_status = 'approved'
        db.session.commit()
        logger.info(f'Mentor {mentor_id} approved successfully')
        return {'success': True}
    except Exception as e:
        logger.error(f'Error approving mentor {mentor_id}: {str(e)}')
        logger.exception(e)
        db.session.rollback()
        return {'success': False, 'error': str(e)}, 500

@admin_dashboard_bp.route('/mentors/<int:mentor_id>/revoke', methods=['POST'])
def revoke_mentor(mentor_id):
    if 'access_token' not in session:
        logger.error(f'Unauthorized access to revoke mentor {mentor_id} by {request.remote_addr}')
        return {'success': False, 'error': 'Unauthorized'}, 401
    
    try:
        mentor = db.session.query(MentorProfile).filter(MentorProfile.id == str(mentor_id)).first()
        if not mentor:
            logger.warning(f'Mentor {mentor_id} not found')
            return {'success': False, 'error': 'Mentor not found'}, 404
            
        mentor.application_status = 'revoked'
        logger.info(f'Revoking mentor {mentor_id} for {session.get("username")}')
        db.session.commit()
        logger.info(f'Mentor {mentor_id} approval revoked successfully')
        return {'success': True}
    except Exception as e:
        logger.error(f'Error revoking mentor {mentor_id}: {str(e)}')
        logger.exception(e)
        db.session.rollback()
        return {'success': False, 'error': str(e)}, 500

from flask import render_template, current_app, Blueprint, request, redirect, url_for, flash, session
from extensions.database import db
from flask_app.models.user import MentorProfile
from extensions.cognito import require_auth, CognitoBackendAuthorizer
from extensions.logging import logger
from sqlalchemy import text
from os import path

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
    if request.method == 'GET' and 'access_token' in session:
        return redirect(url_for('admin.admin_dashboard.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required')
            return render_template('dashboard/login.html')
            
        cognito = CognitoBackendAuthorizer()
        try:
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
            return render_template('dashboard/login.html')
            
    return render_template('dashboard/login.html')


@admin_dashboard_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin.index'))


@admin_dashboard_bp.route('/dashboard')
def dashboard():
    if 'access_token' not in session:
        return redirect(url_for('admin.admin_dashboard.index'))
    """Admin dashboard showing system status"""
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        db_status = "Successfully connected to database"
    except Exception as e:
        db_status = f"Database connection failed: {str(e)}"

    return render_template('dashboard/index.html', db_status=db_status)

@admin_dashboard_bp.route('/mentors')
def mentors():
    if 'access_token' not in session:
        return redirect(url_for('admin.admin_dashboard.index'))
    """Admin dashboard showing all mentor profiles"""
    mentors = db.session.query(MentorProfile).all()
    return render_template('dashboard/mentors.html', mentors=mentors)

@admin_dashboard_bp.route('/mentors/<int:mentor_id>/approve', methods=['POST'])
def approve_mentor(mentor_id):
    if 'access_token' not in session:
        return {'success': False, 'error': 'Unauthorized'}, 401
    
    try:
        mentor = db.session.query(MentorProfile).get(mentor_id)
        if not mentor:
            return {'success': False, 'error': 'Mentor not found'}, 404
            
        mentor.application_status = 'approved'
        db.session.commit()
        logger.info(f'Mentor {mentor_id} approved successfully')
        return {'success': True}
    except Exception as e:
        logger.error(f'Error approving mentor {mentor_id}: {str(e)}')
        db.session.rollback()
        return {'success': False, 'error': str(e)}, 500

@admin_dashboard_bp.route('/mentors/<int:mentor_id>/revoke', methods=['POST'])
def revoke_mentor(mentor_id):
    if 'access_token' not in session:
        return {'success': False, 'error': 'Unauthorized'}, 401
    
    try:
        mentor = db.session.query(MentorProfile).get(mentor_id)
        if not mentor:
            return {'success': False, 'error': 'Mentor not found'}, 404
            
        mentor.application_status = 'revoked'
        db.session.commit()
        logger.info(f'Mentor {mentor_id} approval revoked successfully')
        return {'success': True}
    except Exception as e:
        logger.error(f'Error revoking mentor {mentor_id}: {str(e)}')
        db.session.rollback()
        return {'success': False, 'error': str(e)}, 500

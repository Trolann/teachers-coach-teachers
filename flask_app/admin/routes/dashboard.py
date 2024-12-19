from flask import render_template, current_app, Blueprint, request, redirect, url_for, flash, session
from extensions.cognito import require_auth, CognitoBackendAuthorizer
from sqlalchemy import text
from os import path

# Get the current directory path
current_dir = path.dirname(path.abspath(__file__))
template_dir = path.join(current_dir, '..', 'templates')

# Create blueprint with template folder specified
admin_dashboard_bp = Blueprint('admin_dashboard', __name__,
                             template_folder=template_dir)


@admin_dashboard_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required')
            return render_template('dashboard/login.html')
            
        cognito = CognitoBackendAuthorizer()
        try:
            response = cognito.login(username, password)
            if 'error' in response:
                print(f'{response}')
                flash(f'Login failed: {response["error"]}')
                return render_template('dashboard/login.html')
                
            # Store the access token
            session['access_token'] = response['AccessToken']
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
@require_auth
def dashboard():
    """Admin dashboard showing system status"""
    try:
        # Test database connection
        current_app.db.session.execute(text('SELECT 1'))
        db_status = "Successfully connected to database"
    except Exception as e:
        db_status = f"Database connection failed: {str(e)}"

    return render_template('dashboard/index.html', db_status=db_status)

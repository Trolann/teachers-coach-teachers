from flask import render_template, current_app, Blueprint, request, redirect, url_for, flash, session
from extensions.cognito import require_auth, CognitoAuthTester
from sqlalchemy import text

admin_dashboard_bp = Blueprint('admin_dashboard', __name__)


@admin_dashboard_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required')
            return render_template('dashboard/login.html')
            
        cognito = CognitoAuthTester()
        try:
            response = cognito.simulate_login(username, password)
            if 'error' in response:
                flash(f'Login failed: {response["error"]}')
                return render_template('dashboard/login.html')
                
            # Store the access token
            session['access_token'] = response['AccessToken']
            return redirect(url_for('admin.dashboard'))
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

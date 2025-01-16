from flask import Blueprint, render_template, request, flash, session, redirect, url_for, jsonify
from extensions.logging import get_logger
from os import path
from models.credits import CreditRedemption, CreditTransfer
from models.user import User
from extensions.database import db
from extensions.cognito import require_auth

logger = get_logger(__name__)

# Get the current directory path
current_dir = path.dirname(path.abspath(__file__))
template_dir = path.join(current_dir, '..', 'templates')
static_dir = path.join(current_dir, '..', 'static')

# Create blueprint with template folder specified
admin_credits_bp = Blueprint('admin_credits', __name__,
                               static_folder=static_dir,
                               static_url_path='/admin/static',
                               template_folder=template_dir)


@admin_credits_bp.route('/search-users', methods=['GET'])
@require_auth
def search_users():
    """Search users by email"""
    query = request.args.get('q', '').lower()
    
    # If query is empty, return first 10 users
    if not query:
        users = User.query.limit(10).all()
    else:
        users = User.query.filter(User.email.ilike(f'%{query}%')).limit(10).all()
    return jsonify([{
        'email': user.email,
        'id': user.id
    } for user in users])

@admin_credits_bp.route('/', methods=['GET', 'POST'])
@require_auth
def index():
    """Handle credit code generation and display"""
    if 'access_token' not in session:
        logger.debug('Unauthorized access attempt to credits page')
        return redirect(url_for('admin.admin_dashboard.index'))

    logger.debug('Rendering admin credits page')
    
    if request.method == 'POST':
        if 'access_token' not in session:
            logger.warning(f'Unauthorized code generation attempt from {request.remote_addr}')
            return redirect(url_for('admin.admin_dashboard.index'))

    # Get all credit codes for display
    credit_codes = CreditRedemption.query.order_by(CreditRedemption.created_at.desc()).all()
    return render_template('dashboard/credits.html', credit_codes=credit_codes)

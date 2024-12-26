from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from extensions.logging import get_logger
from os import path
from models.credits import CreditRedemption, CreditTransfer
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
        try:
            num_codes = int(request.form.get('num_codes', 1))
            credits_per_code = int(request.form.get('credits_per_code', 0))
            admin_id = session.get('user_id')
            
            if not admin_id:
                logger.error('Admin ID not found in session')
                flash('Authentication error', 'error')
                return redirect(url_for('admin.admin_dashboard.index'))
            
            if credits_per_code <= 0:
                flash('Credits per code must be greater than 0', 'error')
            elif num_codes <= 0:
                flash('Number of codes must be greater than 0', 'error')
            else:
                # Generate the requested number of codes
                for _ in range(num_codes):
                    redemption = CreditRedemption(
                        created_by=admin_id,
                        amount=credits_per_code
                    )
                    db.session.add(redemption)
                
                db.session.commit()
                flash(f'Successfully generated {num_codes} credit codes', 'success')
                
        except ValueError:
            flash('Please enter valid numbers', 'error')
        except Exception as e:
            logger.error(f"Error generating codes: {e}")
            flash('An error occurred while generating codes', 'error')
            db.session.rollback()

    # Get all credit codes for display
    credit_codes = CreditRedemption.query.order_by(CreditRedemption.created_at.desc()).all()
    
    return render_template('dashboard/credits.html', credit_codes=credit_codes)

from flask import Blueprint, request, jsonify
from extensions.logging import get_logger
from models.credits import CreditRedemption
from models.user import User
from extensions.database import db
from extensions.cognito import require_auth

logger = get_logger(__name__)

credits_bp = Blueprint('credits', __name__)

@credits_bp.route('/redeem', methods=['POST'])
#@require_auth
def redeem_credit():
    """Redeem a credit code for a user"""
    data = request.get_json()
    code = data.get('code')
    user_identifier = data.get('user_identifier')  # Can be cognito_sub or email
    logger.debug(f'Redeeming credit code {code} for user {user_identifier}')
    if not code or not user_identifier:
        return jsonify({'error': 'Missing required fields'}), 400
        
    # Find the credit code
    credit = CreditRedemption.query.filter_by(code=code, redeemed_by=None).first()
    if not credit:
        return jsonify({'error': 'Invalid or already redeemed code'}), 400
        
    # Find the user by cognito_sub or email
    user = User.query.filter(
        (User.cognito_sub == user_identifier) | 
        (User.email == user_identifier)
    ).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    try:
        # Update user's credits
        user.credits = (user.credits or 0) + credit.amount
        credit.redeemed_by = user.id
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully redeemed {credit.amount} credits',
            'new_balance': user.credits
        })
        
    except Exception as e:
        logger.error(f"Error redeeming credits: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to redeem credits'}), 500

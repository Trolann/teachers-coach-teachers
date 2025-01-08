from flask import Blueprint, request, jsonify, session
from extensions.logging import get_logger
from models.credits import CreditRedemption
from models.user import User
from extensions.database import db
from extensions.cognito import require_auth, CognitoTokenVerifier

logger = get_logger(__name__)

credits_bp = Blueprint('credits', __name__)

@credits_bp.route('/generate', methods=['POST'])
@require_auth
def generate_credits():
    """Generate credit codes - currently admin only"""
    data = request.get_json()
    num_codes = data.get('num_codes', 1)
    credits_per_code = data.get('credits_per_code', 0)
    admin_id = session.get('user_id')

    if not admin_id:
        return jsonify({'error': 'Authentication required'}), 401

    # TODO: Add user role validation when implementing user-generated credits
    # For now, only admins can generate credits
    cognito = CognitoTokenVerifier()
    if not cognito.is_user_admin(session.get('access_token')):
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        if credits_per_code <= 0:
            return jsonify({'error': 'Credits per code must be greater than 0'}), 400
        elif num_codes <= 0:
            return jsonify({'error': 'Number of codes must be greater than 0'}), 400

        generated_codes = []
        for _ in range(num_codes):
            redemption = CreditRedemption(
                created_by=admin_id,
                amount=credits_per_code
            )
            db.session.add(redemption)
            generated_codes.append({
                'code': redemption.code,
                'amount': redemption.amount
            })
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': f'Successfully generated {num_codes} credit codes',
            'codes': generated_codes
        })

    except Exception as e:
        logger.error(f"Error generating codes: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to generate codes'}), 500

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
            'new_balance': user.credits,
            'code': code,
            'redeemed_at': credit.redeemed_at.strftime('%Y-%m-%d %H:%M:%S') if credit.redeemed_at else None
        })
        
    except Exception as e:
        logger.error(f"Error redeeming credits: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to redeem credits'}), 500

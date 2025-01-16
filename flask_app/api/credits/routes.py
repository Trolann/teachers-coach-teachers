from flask import Blueprint, request, jsonify, session
from extensions.logging import get_logger
from models.credits import CreditRedemption, CreditPool
from models.user import User
from extensions.database import db
from extensions.cognito import require_auth, CognitoTokenVerifier
from datetime import datetime

logger = get_logger(__name__)

credits_bp = Blueprint('credits', __name__)

def require_district_admin(f):
    """Decorator to check if user is a district admin"""
    def decorated(*args, **kwargs):
        if 'access_token' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        cognito = CognitoTokenVerifier()
        if not cognito._check_user_group(session.get('access_token'), 'district_admin'):
            return jsonify({'error': 'District admin privileges required'}), 403
            
        return f(*args, **kwargs)
    return decorated

@credits_bp.route('/pools', methods=['GET'], endpoint='list_pools')
@require_district_admin
def list_pools():
    """List credit pools owned by the current user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    try:
        pools = CreditPool.query.filter_by(owner_id=user_id).all()
        return jsonify({
            'pools': [{
                'id': pool.id,
                'name': pool.name,
                'code': pool.pool_code,
                'created_at': pool.created_at.isoformat(),
                'is_active': pool.is_active,
                'credits_available': pool.credits_available
            } for pool in pools]
        })
    except Exception as e:
        logger.error(f"Error listing pools: {e}")
        return jsonify({'error': 'Failed to list pools'}), 500

@credits_bp.route('/pools', methods=['POST'], endpoint='create_pool')
@require_district_admin
def create_pool():
    """Create a new credit pool"""
    data = request.get_json()
    name = data.get('name')
    initial_credits = data.get('initial_credits', 0)
    
    if not name:
        return jsonify({'error': 'Pool name is required'}), 400
        
    try:
        pool = CreditPool(
            name=name,
            owner_id=session.get('user_id')
        )
        db.session.add(pool)
        db.session.commit()
        
        return jsonify({
            'message': 'Pool created successfully',
            'pool': {
                'id': pool.id,
                'name': pool.name,
                'code': pool.pool_code
            }
        })
    except Exception as e:
        logger.error(f"Error creating pool: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create pool'}), 500

@credits_bp.route('/pools/<int:pool_id>', methods=['PUT'], endpoint='update_pool')
@require_district_admin
def update_pool(pool_id):
    """Update a credit pool"""
    pool = CreditPool.query.get(pool_id)
    if not pool:
        return jsonify({'error': 'Pool not found'}), 404
        
    if pool.owner_id != session.get('user_id'):
        return jsonify({'error': 'Unauthorized to modify this pool'}), 403
        
    data = request.get_json()
    try:
        if 'name' in data:
            pool.name = data['name']
        if 'is_active' in data:
            pool.is_active = data['is_active']
            
        db.session.commit()
        return jsonify({
            'message': 'Pool updated successfully',
            'pool': {
                'id': pool.id,
                'name': pool.name,
                'is_active': pool.is_active
            }
        })
    except Exception as e:
        logger.error(f"Error updating pool: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update pool'}), 500

@credits_bp.route('/pools/<int:pool_id>/users', methods=['POST'], endpoint='add_user_to_pool')
@require_district_admin
def add_user_to_pool(pool_id):
    """Add a user to a credit pool"""
    pool = CreditPool.query.get(pool_id)
    if not pool:
        return jsonify({'error': 'Pool not found'}), 404
        
    if pool.owner_id != session.get('user_id'):
        return jsonify({'error': 'Unauthorized to modify this pool'}), 403
        
    data = request.get_json()
    user_identifier = data.get('user_identifier')  # email or cognito_sub
    
    if not user_identifier:
        return jsonify({'error': 'User identifier required'}), 400
        
    try:
        user = User.query.filter(
            (User.email == user_identifier) |
            (User.cognito_sub == user_identifier)
        ).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        if user in pool.users:
            return jsonify({'error': 'User already in pool'}), 400
            
        pool.users.append(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User added to pool successfully',
            'user': {
                'id': user.id,
                'email': user.email
            }
        })
    except Exception as e:
        logger.error(f"Error adding user to pool: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to add user to pool'}), 500

@credits_bp.route('/pools/<int:pool_id>/users/<int:user_id>', methods=['DELETE'], endpoint='remove_user_from_pool')
@require_district_admin
def remove_user_from_pool(pool_id, user_id):
    """Remove a user from a credit pool"""
    pool = CreditPool.query.get(pool_id)
    if not pool:
        return jsonify({'error': 'Pool not found'}), 404
        
    if pool.owner_id != session.get('user_id'):
        return jsonify({'error': 'Unauthorized to modify this pool'}), 403
        
    try:
        user = User.query.get(user_id)
        if not user or user not in pool.users:
            return jsonify({'error': 'User not in pool'}), 404
            
        pool.users.remove(user)
        db.session.commit()
        
        return jsonify({'message': 'User removed from pool successfully'})
    except Exception as e:
        logger.error(f"Error removing user from pool: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to remove user from pool'}), 500

@credits_bp.route('/generate', methods=['POST'], endpoint='generate_credits')
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

@credits_bp.route('/debug/session', methods=['GET'])
@require_district_admin
def debug_session():
    """Debug endpoint to check session contents"""
    return jsonify({
        'session_contents': {k: v for k, v in session.items()},
        'user_id': session.get('user_id'),
        'email': session.get('email'),
        'access_token': bool(session.get('access_token'))  # Just return if present
    })

@credits_bp.route('/redeem', methods=['POST'], endpoint='redeem_credit')
@require_district_admin
def redeem_credit():
    """Redeem a credit code to a credit pool"""
    data = request.get_json()
    code = data.get('code')
    pool_id = data.get('pool_id')
    verifier = CognitoTokenVerifier()
    user_info = verifier.get_user_attributes(session.get('access_token'))
    
    if not code or not pool_id:
        return jsonify({'error': 'Missing required fields'}), 400
        
    try:
        # Start a transaction with strong isolation
        db.session.begin_nested()
        
        # Find and lock the credit code for update
        credit = CreditRedemption.query.filter_by(code=code, credit_pool_id=None)\
            .with_for_update().first()
        if not credit:
            return jsonify({'error': 'Invalid or already redeemed code'}), 400
            
        # Find and lock the pool for update
        pool = CreditPool.query.filter_by(id=pool_id)\
            .with_for_update().first()
        if not pool:
            return jsonify({'error': 'Pool not found'}), 404
            
        # Verify pool ownership
        if pool.owner_id != session.get('user_id'):
            return jsonify({'error': 'Unauthorized to redeem to this pool'}), 403

        # Add credits to pool
        if pool.credits_available is None:
            pool.credits_available = 0
            
        # Get user email from session and ensure it exists
        user_email = user_info.get('email')
        if not user_email:
            logger.error("No email found in session during redemption")
            return jsonify({'error': 'User email not found in session'}), 400

        logger.info(f"Attempting redemption with email: {user_email}")
        
        pool.credits_available += credit.amount
        credit.credit_pool_id = pool.id
        credit.redeemed_at = datetime.utcnow()
        credit.redeemed_by_email = user_email  # This should be a string field in the DB
        
        # Log state before commit
        logger.info(f"Pre-commit state - Pool {pool_id}: credits_available={pool.credits_available}, "
                   f"code: {code}, redeemed_by_email: {credit.redeemed_by_email}")
        
        # Commit the nested transaction
        db.session.commit()
        
        # Verify the changes after commit
        db.session.refresh(credit)
        db.session.refresh(pool)
        
        # Log final state with more details
        logger.info(f"Successfully redeemed code {code} for {credit.amount} credits to pool {pool_id}. "
                   f"Final state - redeemed_by_email: {credit.redeemed_by_email}, "
                   f"credits_available: {pool.credits_available}, "
                   f"credit_pool_id: {credit.credit_pool_id}, "
                   f"redeemed_at: {credit.redeemed_at}")
        
        return jsonify({
            'success': True,
            'message': f'Successfully added {credit.amount} credits to pool',
            'pool': {
                'id': pool.id,
                'name': pool.name,
                'credits_available': pool.credits_available
            },
            'code': code,
            'redeemed_at': credit.redeemed_at.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error redeeming credits to pool: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to redeem credits'}), 500


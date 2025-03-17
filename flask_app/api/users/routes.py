from flask import Blueprint, request, jsonify
from models.user import User, UserType, ApplicationStatus
from extensions.database import db
from extensions.logging import get_logger
from extensions.cognito import require_auth, parse_headers, CognitoTokenVerifier
from datetime import datetime
from typing import Optional

user_bp = Blueprint('users', __name__, url_prefix='/api/users')
verifier = CognitoTokenVerifier()
logger = get_logger(__name__)

def get_user_from_token(headers) -> Optional[User]:
    """
    Helper function to get user from token
    
    Args:
        headers: The request headers containing the authentication token
        
    Returns:
        User object if found, None otherwise
    """
    auth_token = parse_headers(headers)[0]
    if not auth_token:
        logger.warning("No auth token found in headers")
        return None
    
    user_info = verifier.get_user_attributes(auth_token)
    if not user_info or 'sub' not in user_info:
        logger.warning("Invalid user info from token")
        return None
    
    user = User.get_by_id(user_info['sub'])
    if not user:
        logger.warning(f"User with cognito_sub {user_info['sub']} not found")
    
    return user

@user_bp.route('/submit_application', methods=['POST'])
@require_auth
def submit_application():
    """Submit a user application"""
    user = get_user_from_token(request.headers)
    if not user:
        return jsonify({'error': 'User not found or invalid token'}), 401

    # Get JSON data from request
    profile_data = request.get_json()
    if not profile_data:
        return jsonify({'error': 'No profile data provided'}), 400

    # Check if user is already a mentor
    if user.user_type == UserType.MENTOR:
        return jsonify({'error': 'Application already exists'}), 409

    # Update user to be a mentor
    user.user_type = UserType.MENTOR
    user.update_profile(profile_data)
    user.application_status = ApplicationStatus.PENDING
    db.session.commit()
    
    logger.info(f"Application submitted for user: {user.cognito_sub}")

    return jsonify({
        'message': 'Application submitted successfully',
        'user_id': user.cognito_sub,
        'status': user.application_status.value
    }), 201

@user_bp.route('/update_application', methods=['POST'])
@require_auth
def update_application():
    """Update a user application"""
    user = get_user_from_token(request.headers)
    if not user:
        return jsonify({'error': 'User not found or invalid token'}), 401

    # Get JSON data from request
    profile_data = request.get_json()
    if not profile_data:
        return jsonify({'error': 'No profile data provided'}), 400

    # Check if user is a mentor
    if user.user_type != UserType.MENTOR:
        return jsonify({'error': 'No application found'}), 404

    # Only allow updates if application is pending
    if user.application_status != ApplicationStatus.PENDING:
        return jsonify({'error': 'Cannot update application in current status'}), 403

    # Update profile data using the model's method
    user.update_profile(profile_data)
    db.session.commit()
    
    logger.info(f"Application updated for user: {user.cognito_sub}")

    return jsonify({
        'message': 'Application updated successfully',
        'user_id': user.cognito_sub,
        'status': user.application_status.value
    })

@user_bp.route('/get_application', methods=['GET'])
@require_auth
def get_application():
    """Get a user application"""
    user = get_user_from_token(request.headers)
    if not user:
        return jsonify({'error': 'User not found or invalid token'}), 401

    if user.user_type != UserType.MENTOR:
        return jsonify({'error': 'No application found'}), 404
    
    logger.debug(f"Application retrieved for user: {user.cognito_sub}")

    return jsonify({
        'user_id': user.cognito_sub,
        'status': user.application_status.value,
        'submitted_at': user.created_at.isoformat(),
        'profile_data': user.profile
    })

@user_bp.route('/get_application_status', methods=['GET'])
@require_auth
def get_application_status():
    """Get the status of a user application"""
    user = get_user_from_token(request.headers)
    if not user:
        return jsonify({'error': 'User not found or invalid token'}), 401

    if user.user_type != UserType.MENTOR:
        return jsonify({'error': 'No application found'}), 404
    
    logger.debug(f"Application status retrieved for user: {user.cognito_sub}")

    return jsonify({
        'user_id': user.cognito_sub,
        'status': user.application_status.value,
        'submitted_at': user.created_at.isoformat()
    })

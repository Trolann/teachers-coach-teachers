from flask import Blueprint, request, jsonify
from models.user import User, UserType, ApplicationStatus
from extensions.database import db
from extensions.logging import get_logger
from extensions.cognito import require_auth, parse_headers, CognitoTokenVerifier
from extensions.embeddings import EmbeddingFactory
from datetime import datetime
from typing import Optional

user_bp = Blueprint('users', __name__, url_prefix='/api/users')
verifier = CognitoTokenVerifier()
logger = get_logger(__name__)
embedding_factory = EmbeddingFactory()

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
    logger.debug(f'User info: {user_info}')
    
    # Try to get user_id from 'sub' field (standard JWT claim)
    user_id = user_info.get('sub')
    if not user_id:
        # Fallback to 'user_id' field if 'sub' is not present
        user_id = user_info.get('user_id')
        
    if not user_id:
        logger.warning("Invalid user info from token - no user identifier found")
        return None
    
    user = User.get_by_id(user_id)
    if not user:
        logger.warning(f"User with cognito_sub {user_id} not found")
    
    return user

@user_bp.route('/submit_application', methods=['POST'])
@require_auth
def submit_application():
    """Submit a user application"""
    user = get_user_from_token(request.headers)
    if not user:
        logger.debug(f'User not found or invalid token {request.headers}')
        return jsonify({'error': 'User not found or invalid token'}), 401

    # Get JSON data from request
    profile_data = request.get_json()

    # Extract user_type from profile_data
    user_type = profile_data.get('user_type')
    if user_type:
        logger.info(f'Got user_type from profile_data: {user_type} {type(user_type)}')
        profile_data.pop('user_type')

    logger.info(f'Profile data received: {profile_data}')
    if not profile_data:
        return jsonify({'error': 'No profile data provided'}), 400


    # Update user to be a mentor
    found = False
    if user_type == "MENTEE":
        user.user_type = UserType.MENTEE
        found = True
        logger.debug(f"User type set to MENTEE")
    if user_type == "MENTOR":
        user.user_type = UserType.MENTOR
        found = True
        logger.debug(f"User type set to MENTOR")
    if user_type == "ADMIN":
        # TODO: require_auth should add an is_admin header
        return jsonify({'error': 'Unable to set profile applications for ADMIN users'}), 400
    if not found:
        logger.warn(f"Invalid user_type {user_type}")
        logger.debug(f'User type: {user.user_type} {type(user.user_type)}')
        logger.debug(f'user_type == "ADMIN" {user_type == "ADMIN"}')
        return jsonify({'error': 'Invalid user type'}), 400

    # check if there's already a profile, error out if there is
    if user.profile or user.application_status != ApplicationStatus.PENDING:
        logger.info(f'User already has a profile or application status is not PENDING')
        return jsonify({'error': 'Application already submitted.'}), 403

    user.application_status = ApplicationStatus.PENDING
    if user.user_type == 'MENTEE':
        user.application_status = ApplicationStatus.APPROVED
        embedding_factory.store_embedding(user.cognito_sub, profile_data)
    user.profile = profile_data
    db.session.commit()

    logger.info(f"Application submitted for user: {user.cognito_sub} with profile: {user.profile}")

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
    logger.info(f'Update profile data received: {profile_data}')
    if not profile_data:
        return jsonify({'error': 'No profile data provided'}), 400


    # Get the current profile and update it with new data
    current_profile = user.profile or {}
    current_profile.update(profile_data)

    # Set the updated profile
    user.profile = {}
    db.session.commit() # Clear profile first
    user.profile = current_profile
    user.application_status = ApplicationStatus.PENDING if user.user_type == 'MENTOR' else ApplicationStatus.APPROVED
    db.session.commit()
    
    logger.info(f"Application updated for user: {user.cognito_sub} with profile: {user.profile}")

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

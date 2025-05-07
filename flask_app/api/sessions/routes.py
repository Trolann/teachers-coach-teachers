from flask import Blueprint, request, jsonify
from models.user import User
from models.mentorship_session import MentorshipSession, SessionStatus
from extensions.database import db
from extensions.logging import get_logger
from extensions.cognito import require_auth, parse_headers, CognitoTokenVerifier
from datetime import datetime
from typing import Optional

sessions_bp = Blueprint('sessions', __name__)

verifier = CognitoTokenVerifier()
logger = get_logger(__name__)

def get_user_from_token(headers) -> Optional[User]:
    logger.info("Attempting to get user from token")
    auth_token = parse_headers(headers)[0]
    if not auth_token:
        logger.warning("No auth token found in headers")
        return None

    logger.info("Verifying token and getting user attributes")
    user_info = verifier.get_user_attributes(auth_token)
    logger.debug(f'User info: {user_info}')

    user_id = user_info.get('sub') or user_info.get('user_id')
    if not user_id:
        logger.warning("Invalid user info from token - no user identifier found")
        return None

    logger.info(f"Looking up user with ID: {user_id}")
    user = User.get_by_id(user_id)
    if not user:
        logger.warning(f"User with cognito_sub {user_id} not found")
    else:
        logger.info(f"User found: {user.id}")

    return user

@sessions_bp.route('/create', methods=['POST'])
@require_auth
def create_session():
    """Create a new mentorship session"""
    logger.info("Received request to create mentorship session")
    
    user = get_user_from_token(request.headers)
    if not user:
        logger.error("Failed to create session: User not found or invalid token")
        return jsonify({'error': 'User not found or invalid token'}), 401

    logger.info(f"Authenticated user: {user.id}")
    
    data = request.get_json()
    if not data:
        logger.error("Failed to create session: No session data provided")
        return jsonify({'error': 'No session data provided'}), 400

    logger.debug(f"Session creation data: {data}")

    # Required fields
    required_fields = ['mentor_id', 'mentee_id', 'scheduled_datetime', 'duration_minutes']
    for field in required_fields:
        if field not in data:
            logger.error(f"Failed to create session: Missing required field: {field}")
            return jsonify({'error': f'Missing required field: {field}'}), 400

    try:
        logger.info(f"Parsing scheduled datetime: {data['scheduled_datetime']}")
        # Parse the datetime
        scheduled_datetime = datetime.fromisoformat(data['scheduled_datetime'])
        
        logger.info(f"Creating mentorship session between mentor {data['mentor_id']} and mentee {data['mentee_id']}")
        # Create the mentorship session
        session = MentorshipSession(
            mentee_id=data['mentee_id'],
            mentor_id=data['mentor_id'],
            scheduled_datetime=scheduled_datetime,
            duration_minutes=data['duration_minutes']
        )
        
        # Add optional metadata if provided
        if 'meta_data' in data:
            logger.debug(f"Adding metadata to session: {data['meta_data']}")
            session.meta_data = data['meta_data']
            
        logger.info("Committing session to database")
        db.session.add(session)
        db.session.commit()

            # TODO: we know feedback is good - from models.credits.impport (do the db stuff to transfer the credits)
            # most likely enough to just do a credit transfer method (under models CreditTransfer) else look at CreditPools
        
        logger.info(f"Session created successfully with ID: {session.id}")
        return jsonify({
            'message': 'Mentorship session created successfully',
            'session_id': session.id,
            'status': session.status.value
        }), 201
        
    except ValueError as e:
        logger.error(f"Error parsing datetime: {e}")
        return jsonify({'error': 'Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sessions_bp.route('/<session_id>', methods=['GET'])
@require_auth
def get_session(session_id):
    """Get a specific mentorship session"""
    logger.info(f"Received request to get session with ID: {session_id}")
    
    user = get_user_from_token(request.headers)
    if not user:
        logger.error("Failed to get session: User not found or invalid token")
        return jsonify({'error': 'User not found or invalid token'}), 401

    logger.info(f"Looking up session with ID: {session_id}")
    session = MentorshipSession.query.get(session_id)
    if not session:
        logger.error(f"Session with ID {session_id} not found")
        return jsonify({'error': 'Mentorship session not found'}), 404

    logger.info(f"Checking authorization for user {user.cognito_sub} to view session {session_id}")
    # Check if user is authorized to view this session
    if user.cognito_sub not in {session.mentor_id, session.mentee_id}:
        logger.warning(f"User {user.cognito_sub} unauthorized to view session {session_id}")
        return jsonify({'error': 'Unauthorized to view this session'}), 403

    logger.info(f"Returning session data for session {session_id}")
    return jsonify({
        'id': session.id,
        'mentor_id': session.mentor_id,
        'mentee_id': session.mentee_id,
        'scheduled_datetime': session.scheduled_datetime.isoformat(),
        'duration_minutes': session.duration_minutes,
        'status': session.status.value,
        'mentor_feedback': session.mentor_feedback,
        'mentee_feedback': session.mentee_feedback,
        'meta_data': session.meta_data,
        'created_at': session.created_at.isoformat(),
        'updated_at': session.updated_at.isoformat()
    })

@sessions_bp.route('/list', methods=['GET'])
@require_auth
def list_sessions():
    """List all mentorship sessions for the current user"""
    logger.info("Received request to list sessions")
    
    user = get_user_from_token(request.headers)
    if not user:
        logger.error("Failed to list sessions: User not found or invalid token")
        return jsonify({'error': 'User not found or invalid token'}), 401

    # Get query parameters
    status = request.args.get('status')
    role = request.args.get('role', 'both')  # 'mentor', 'mentee', or 'both'
    
    logger.info(f"Filtering sessions by status: {status}, role: {role}")
    
    # Build the query
    query = MentorshipSession.query
    
    if status:
        try:
            status_enum = SessionStatus[status.upper()]
            logger.debug(f"Filtering by status: {status_enum.value}")
            query = query.filter_by(status=status_enum)
        except KeyError:
            logger.error(f"Invalid status value: {status}")
            return jsonify({'error': f'Invalid status value: {status}'}), 400
    
    if role == 'mentor':
        logger.debug(f"Filtering for sessions where user {user.cognito_sub} is mentor")
        query = query.filter_by(mentor_id=user.cognito_sub)
    elif role == 'mentee':
        logger.debug(f"Filtering for sessions where user {user.cognito_sub} is mentee")
        query = query.filter_by(mentee_id=user.cognito_sub)
    else:  # 'both' or any other value
        logger.debug(f"Filtering for sessions where user {user.cognito_sub} is either mentor or mentee")
        query = query.filter((MentorshipSession.mentor_id == user.cognito_sub) | 
                             (MentorshipSession.mentee_id == user.cognito_sub))
    
    # Order by scheduled date, most recent first
    sessions = query.order_by(MentorshipSession.scheduled_datetime.desc()).all()
    
    logger.info(f"Found {len(sessions)} sessions matching the criteria")
    
    return jsonify({
        'sessions': [{
            'id': session.id.value,
            'mentor_id': session.mentor_id.value,
            'mentee_id': session.mentee_id.value,
            'scheduled_datetime': session.scheduled_datetime.isoformat(),
            'duration_minutes': session.duration_minutes,
            'status': session.status.value,
            'created_at': session.created_at.isoformat(),
        } for session in sessions]
    })

@sessions_bp.route('/<session_id>/feedback', methods=['POST'])
@require_auth
def submit_feedback(session_id):
    """Submit feedback for a mentorship session"""
    logger.info(f"Received request to submit feedback for session {session_id}")
    
    user = get_user_from_token(request.headers)
    if not user:
        logger.error("Failed to submit feedback: User not found or invalid token")
        return jsonify({'error': 'User not found or invalid token'}), 401

    data = request.get_json()
    feedback_data = data.get('feedback_data', {})
    feedback_type = data.get('feedback_type', 'mentee_feedback')
    
    logger.debug(f"Feedback type: {feedback_type}")

    if not feedback_data:
        logger.error("Failed to submit feedback: No feedback data provided")
        return jsonify({'error': 'Feedback data is required'}), 400

    logger.info(f"Looking up session with ID: {session_id}")
    mentorship_session = MentorshipSession.query.get(session_id)
    if not mentorship_session:
        logger.error(f"Session with ID {session_id} not found")
        return jsonify({'error': 'Mentorship session not found'}), 404

    logger.info(f"Checking authorization for user {user.cognito_sub} to submit feedback for session {session_id}")
    if user.cognito_sub not in {mentorship_session.mentor_id, mentorship_session.mentee_id}:
        logger.warning(f"User {user.cognito_sub} unauthorized to submit feedback for session {session_id}")
        return jsonify({'error': 'Unauthorized to submit feedback for this session'}), 403

    if feedback_type == 'mentor_feedback' and user.cognito_sub != mentorship_session.mentor_id:
        logger.warning(f"User {user.cognito_sub} attempted to submit mentor feedback but is not the mentor")
        return jsonify({'error': 'Only the mentor can submit mentor feedback'}), 403
    elif feedback_type == 'mentee_feedback' and user.cognito_sub != mentorship_session.mentee_id:
        logger.warning(f"User {user.cognito_sub} attempted to submit mentee feedback but is not the mentee")
        return jsonify({'error': 'Only the mentee can submit mentee feedback'}), 403

    logger.info(f"Saving {feedback_type} for session {session_id}")
    if feedback_type == 'mentor_feedback':
        mentorship_session.mentor_feedback = feedback_data
    else:
        mentorship_session.mentee_feedback = feedback_data

    if mentorship_session.status == SessionStatus.SCHEDULED:
        logger.info(f"Updating session status to COMPLETED")
        mentorship_session.status = SessionStatus.COMPLETED

    logger.info("Committing feedback to database")
    db.session.commit()

    logger.info(f"Feedback submitted successfully for session {session_id} with the feedback {feedback_type}")
    # TODO: we know feedback is good - from models.credits.impport (do the db stuff to transfer the credits)
    # most likely enough to just do a credit transfer method (under models CreditTransfer) else look at CreditPools

    return jsonify({
        'message': 'Feedback submitted successfully',
        'session_id': session_id,
        'feedback_type': feedback_type
    })

@sessions_bp.route('/<session_id>/status', methods=['PUT'])
@require_auth
def update_status(session_id):
    """Update the status of a mentorship session"""
    logger.info(f"Received request to update status for session {session_id}")
    
    user = get_user_from_token(request.headers)
    if not user:
        logger.error("Failed to update status: User not found or invalid token")
        return jsonify({'error': 'User not found or invalid token'}), 401

    data = request.get_json()
    new_status = data.get('status')
    if not new_status:
        logger.error("Failed to update status: No status provided")
        return jsonify({'error': 'New status is required'}), 400

    logger.info(f"Attempting to update session {session_id} to status: {new_status}")
    
    try:
        status_enum = SessionStatus[new_status.upper()]
        logger.debug(f"Status enum value: {status_enum.value}")
    except (KeyError, AttributeError):
        logger.error(f"Invalid status value: {new_status}")
        return jsonify({'error': 'Invalid status value'}), 400

    logger.info(f"Looking up session with ID: {session_id}")
    mentorship_session = MentorshipSession.query.get(session_id)
    if not mentorship_session:
        logger.error(f"Session with ID {session_id} not found")
        return jsonify({'error': 'Mentorship session not found'}), 404

    logger.info(f"Checking authorization for user {user.cognito_sub} to update session {session_id}")
    if user.cognito_sub not in {mentorship_session.mentor_id, mentorship_session.mentee_id}:
        logger.warning(f"User {user.cognito_sub} unauthorized to update session {session_id}")
        return jsonify({'error': 'Unauthorized to update this session'}), 403

    logger.info(f"Updating session {session_id} status from {mentorship_session.status.value} to {status_enum.value}")
    mentorship_session.status = status_enum
    db.session.commit()

    logger.info(f"Session {session_id} status updated successfully to {new_status}")
    return jsonify({
        'message': 'Session status updated successfully',
        'session_id': session_id,
        'status': new_status
    })

@sessions_bp.route('/<session_id>', methods=['DELETE'])
@require_auth
def delete_session(session_id):
    """Delete a mentorship session"""
    logger.info(f"Received request to delete session {session_id}")
    
    user = get_user_from_token(request.headers)
    if not user:
        logger.error("Failed to delete session: User not found or invalid token")
        return jsonify({'error': 'User not found or invalid token'}), 401

    logger.info(f"Looking up session with ID: {session_id}")
    session = MentorshipSession.query.get(session_id)
    if not session:
        logger.error(f"Session with ID {session_id} not found")
        return jsonify({'error': 'Mentorship session not found'}), 404

    logger.info(f"Checking authorization for user {user.cognito_sub} to delete session {session_id}")
    # Check if user is authorized to delete this session
    if user.cognito_sub not in {session.mentor_id, session.mentee_id}:
        logger.warning(f"User {user.cognito_sub} unauthorized to delete session {session_id}")
        return jsonify({'error': 'Unauthorized to delete this session'}), 403

    try:
        logger.info(f"Deleting session {session_id}")
        db.session.delete(session)
        db.session.commit()
        logger.info(f"Session {session_id} deleted successfully")
        return jsonify({'message': 'Session deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting session {session_id}: {e}")
        return jsonify({'error': str(e)}), 500
from flask import Blueprint, request, jsonify
from extensions.mentor_online_offline import mentor_status_tracker
from extensions.cognito import require_auth
from flask_app.api.users.routes import get_user_from_token

mentor_status_bp = Blueprint('mentor_status', __name__, url_prefix='/mentor_status')

@mentor_status_bp.route('/set_online', methods=['POST'])
@require_auth
def set_online():
    user = get_user_from_token(request.headers)

    mentor_status_tracker.set_online(user.cognito_sub)
    return jsonify({'message': 'Mentor set to online'}), 200

@mentor_status_bp.route('/set_offline', methods=['POST'])
@require_auth
def set_offline():
    user = get_user_from_token(request.headers)

    mentor_status_tracker.set_offline(user.cognito_sub)
    return jsonify({'message': 'Mentor set to offline'}), 200

@mentor_status_bp.route('/is_online', methods=['GET'])
@require_auth
def is_online():
    user = get_user_from_token(request.headers)

    status = mentor_status_tracker.is_online(user.cognito_sub)
    return jsonify({'online': status}), 200

@mentor_status_bp.route('/all_online', methods=['GET'])
def get_all_online():
    return jsonify({'online_mentors': mentor_status_tracker.get_all_online()}), 200

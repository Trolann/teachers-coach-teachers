from flask import Blueprint, request, jsonify import os
from flask_app.api.users.routes import get_user_from_token

picture_bp = Blueprint('picture_bp', __name__, url_prefix='/pictures')
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'flask_app', 'uploads', 'pictures')

@picture_bp.route('/uploads', methods=['POST'])
@require_auth
def upload_picture():
    user = get_user_from_token(request.headers)
    user_id = user.cognito_sub

    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = f"{user_id}.png"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    return jsonify({'message': 'Profile picture uploaded successfully'}), 200

@picture_bp.route('/me', methods=['GET'])
@require_auth
def get_own_profile_picture():
    user = get_user_from_token(request.headers)
    user_id = user.cognito_sub

    filename = f"{user_id}.png"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(filepath):
        return jsonify({'error': 'Profile picture not found'}), 404

    return send_file(filepath, mimetype='image/png')

@picture_bp.route('/<user_id>', methods=['GET'])
def get_user_profile_picture(user_id):
    filename = f"{user_id}.png"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(filepath):
        return jsonify({'error': 'Profile picture not found'}), 404

    return send_file(filepath, mimetype='image/png')
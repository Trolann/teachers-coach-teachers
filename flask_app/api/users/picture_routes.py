from flask import Blueprint, request, jsonify, send_file
import os
import mimetypes
from extensions.cognito import require_auth
from flask_app.api.users.routes import get_user_from_token

picture_bp = Blueprint('picture_bp', __name__, url_prefix='/pictures')
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'flask_app', 'uploads')

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

    extension = mimetypes.guess_extension(file.mimetype) or '.png'
    filename = f"{user_id}{extension}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    return jsonify({'message': 'Profile picture uploaded successfully'}), 200

@picture_bp.route('/<user_id>', methods=['GET'])
def get_user_profile_picture(user_id):
    filename = f"{user_id}.png"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(filepath):
        return jsonify({'error': 'Profile picture not found'}), 404

    return send_file(filepath, mimetype='image/png')
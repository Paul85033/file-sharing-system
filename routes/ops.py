from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os, uuid
from models import File, db
from utils import allowed_file
from auth import require_user_type

ops_bp = Blueprint('ops', __name__)

@ops_bp.route('/upload', methods=['POST'])
@jwt_required()
@require_user_type('ops')
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded.'}), 400

    file = request.files['file']
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type.'}), 400

    original_filename = secure_filename(file.filename)
    extension = original_filename.rsplit('.', 1)[1]
    unique_filename = f"{uuid.uuid4()}.{extension}"
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(file_path)

    file_record = File(
        filename=unique_filename,
        original_filename=original_filename,
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        uploaded_by=get_jwt_identity(),
        file_type=extension
    )
    db.session.add(file_record)
    db.session.commit()
    return jsonify({'message': 'File uploaded', 'file_id': file_record.id})

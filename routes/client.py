from flask import Blueprint, jsonify, url_for, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta, timezone
from models import File, User, DownloadToken, db
from auth import require_user_type, require_verified_user
from utils import generate_secure_token

client_bp = Blueprint('client', __name__)

@client_bp.route('/files', methods=['GET'])
@jwt_required()
@require_user_type('client')
@require_verified_user
def list_files():
    files = File.query.all()
    return jsonify([{
        'id': f.id,
        'filename': f.original_filename,
        'uploaded_by': User.query.get(f.uploaded_by).username,
        'file_size': f.file_size
    } for f in files])

@client_bp.route('/download-file/<int:file_id>', methods=['GET'])
@jwt_required()
@require_user_type('client')
@require_verified_user
def download_file(file_id):
    file = File.query.get(file_id)
    if not file:
        return jsonify({'error': 'File not found.'}), 404

    token = generate_secure_token()
    download_token = DownloadToken(
        token=token,
        file_id=file.id,
        user_id=get_jwt_identity(),
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    db.session.add(download_token)
    db.session.commit()

    link = url_for('client.secure_download', token=token, _external=True)
    return jsonify({'download_link': link})

@client_bp.route('/download/<token>', methods=['GET'])
def secure_download(token):
    dt = DownloadToken.query.filter_by(token=token).first()
    if not dt or dt.expires_at < datetime.now(timezone.utc) or dt.is_used:
        return jsonify({'error': 'Invalid or expired token.'}), 410

    file = File.query.get(dt.file_id)
    if not file:
        return jsonify({'error': 'File not found.'}), 404

    dt.is_used = True
    db.session.commit()

    return send_file(file.file_path, as_attachment=True, download_name=file.original_filename)

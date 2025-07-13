from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models import db, User
from service import send_verification_email, get_serializer

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/client/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data or not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'Missing fields'}), 400

    if User.query.filter_by(username=data['username']).first() or User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Username or email already exists.'}), 409

    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        user_type='client',
        is_verified=False
    )
    db.session.add(user)
    db.session.commit()

    token = get_serializer().dumps(user.email, salt='email-verify')
    if send_verification_email(user.email, token):
        return jsonify({'message': 'Signup successful, verify your email.'}), 201
    return jsonify({'error': 'Failed to send an email.'}), 500

@auth_bp.route('/client/login', methods=['POST'])
def client_login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username'), user_type='client').first()
    if user and check_password_hash(user.password_hash, data.get('password')):
        if not user.is_verified:
            return jsonify({'error': 'Email not verified.'}), 401
        return jsonify({'access_token': create_access_token(identity=str(user.id))})
    return jsonify({'error': 'Invalid credentials.'}), 401

@auth_bp.route('/ops/login', methods=['POST'])
def ops_login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username'), user_type='ops').first()
    if user and check_password_hash(user.password_hash, data.get('password')):
        return jsonify({'access_token': create_access_token(identity=str(user.id))})
    return jsonify({'error': 'Invalid credentials.'}), 401

@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    try:
        email = get_serializer().loads(token, salt='email-verify', max_age=3600)
        user = User.query.filter_by(email=email).first()
        if user:
            user.is_verified = True
            db.session.commit()
            return jsonify({'message': 'Email verified'})
    except Exception:
        return jsonify({'error': 'Invalid or expired token.'}), 400

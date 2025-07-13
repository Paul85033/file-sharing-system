from flask_jwt_extended import JWTManager, get_jwt_identity
from flask import jsonify
from functools import wraps
from models import User

jwt = JWTManager()

def require_user_type(user_type):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = User.query.get(get_jwt_identity())
            if not user or user.user_type != user_type:
                return jsonify({'error': 'Invalid auth.'}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

def require_verified_user(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = User.query.get(get_jwt_identity())
        if not user or not user.is_verified:
            return jsonify({'error': 'Email verification required.'}), 401
        return f(*args, **kwargs)
    return wrapper

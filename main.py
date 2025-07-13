from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
import os

from config import Config
from db import db
from auth import jwt
from routes.auth import auth_bp
from routes.ops import ops_bp
from routes.client import client_bp

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
jwt.init_app(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(ops_bp, url_prefix='/api/ops')
app.register_blueprint(client_bp, url_prefix='/api/client')

from models import create_default_ops_user
with app.app_context():
    db.create_all()
    create_default_ops_user()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

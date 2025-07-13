Simple and secure file sharing system using Flask and SQLAlchemy.

## Prerequisites for running:

1. Create .env file with the following :

```bash
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=sqlite:///file_sharing.db
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

2. Create a virtual environment and install the requirements with "pip install -r requirements.txt"

3. Run with "python main.py"

4. If using docker, use "docker-compose up --build"


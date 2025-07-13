import secrets

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pptx', 'docx', 'xlsx'}

def generate_secure_token():
    return secrets.token_urlsafe(32)

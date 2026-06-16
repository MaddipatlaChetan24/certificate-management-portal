import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/certificate_portal")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super_secret_fallback_key") # Use a strong key in .env
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "./backend/certificates")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # Max upload size (16MB)
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
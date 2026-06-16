from flask_jwt_extended import JWTManager
from flask_mail import Mail

# Create the extension instances but do not initialize them here
jwt = JWTManager()
mail = Mail()
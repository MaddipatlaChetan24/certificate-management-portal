import os
from flask import Flask, jsonify, send_from_directory
from flask_pymongo import PyMongo
from datetime import timedelta
from flask_cors import CORS

# Imports from your new extensions file
from config import Config
from extensions import jwt, mail 

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # --- *** THIS IS THE CORRECTED LINE *** ---
    # It now correctly sets the token lifetime.
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

    # Initialize extensions with the app
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    jwt.init_app(app) 
    mail.init_app(app)

    # Import and register blueprints
    from routes.auth import auth_bp
    from routes.students import students_bp
    from routes.advisor import advisor_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(students_bp, url_prefix='/api/students')
    app.register_blueprint(advisor_bp, url_prefix='/api/advisors')

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    @app.route('/')
    def hello_world():
        return jsonify(message="Welcome to the Certificate Management Portal!")

    @app.route('/certificates/<filename>')
    def serve_certificate(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
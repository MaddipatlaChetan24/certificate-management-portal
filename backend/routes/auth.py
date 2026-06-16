from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models import User, users_collection
from extensions import jwt, mail
from flask_mail import Message
from config import Config
from datetime import datetime, timedelta
import secrets
from bson.objectid import ObjectId

auth_bp = Blueprint('auth', __name__)

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.find_by_id(identity)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    role = data.get('role')
    password = data.get('password')
    email = data.get('email')
    
    if not role or not password or not email:
        return jsonify({"msg": "Missing required fields"}), 400
    if len(password) < 8:
         return jsonify({"msg": "Password must be at least 8 characters long"}), 400

    username = None
    student_id = None
    if role == 'student':
        student_id = data.get('student_id')
        if not student_id:
            return jsonify({"msg": "Student ID is required for students"}), 400
        username = student_id
    elif role == 'advisor':
        username = email
    else:
        return jsonify({"msg": "Invalid role specified"}), 400
        
    try:
        new_user = User(
            username=username,
            password=password,
            role=role,
            email=email,
            student_id=student_id
        )
        
        # --- THIS IS THE MODIFIED LINE ---
        # It now generates a 6-digit number instead of an alphanumeric code.
        code = str(secrets.randbelow(1000000)).zfill(6)
        
        expiration = datetime.utcnow() + timedelta(minutes=15)

        user_id_str = new_user.save()
        user_id_obj = ObjectId(user_id_str)

        users_collection.update_one(
            {'_id': user_id_obj},
            {'$set': {'verification_code': code, 'code_expiration': expiration}}
        )
        
        # --- DEBUGGING FALLBACK FOR EMAIL ---
        alert_message = f"Registration successful! A verification code has been sent to {email}."
        try:
            msg = Message(
                'Verify Your Account - Certificate Portal',
                sender=Config.MAIL_USERNAME,
                recipients=[email]
            )
            msg.body = f'Welcome!\n\nYour verification code is: {code}\n\nThis code will expire in 15 minutes.'
            mail.send(msg)
        except Exception as e:
            # If email fails, print the code to the console for debugging.
            print("="*60)
            print("!!! EMAIL SENDING FAILED !!!")
            print(f"ERROR: {e}")
            print(f"VERIFICATION CODE for {email} is: {code}")
            print("="*60)
            alert_message = "Registration successful! FAILED to send email. Please check the Flask server console for your verification code."

        return jsonify({"msg": alert_message, "userId": user_id_str}), 201

    except ValueError as e: # Catches duplicate user errors from the model
        return jsonify({"msg": str(e)}), 409 # 409 Conflict is more appropriate
    except Exception as e:
        return jsonify({"msg": f"An internal server error occurred: {str(e)}"}), 500

@auth_bp.route('/verify', methods=['POST'])
def verify_account():
    data = request.get_json()
    user_id = data.get('userId')
    code = data.get('code')

    if not user_id or not code:
        return jsonify({"msg": "User ID and verification code are required"}), 400

    user = User.find_by_id(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    if user.get('is_verified'):
        return jsonify({"msg": "Account is already verified"}), 400

    stored_code = user.get('verification_code')
    code_expiration = user.get('code_expiration')

    if not stored_code or not code_expiration or datetime.utcnow() > code_expiration:
        return jsonify({"msg": "Code has expired or is invalid. Please try registering again."}), 400
    
    # .upper() is harmless here even with digits, so we can leave it
    if stored_code != code.upper():
        return jsonify({"msg": "Invalid verification code"}), 400

    users_collection.update_one(
        {'_id': user['_id']},
        {
            '$set': {'is_verified': True},
            '$unset': {'verification_code': "", 'code_expiration': ""}
        }
    )
    return jsonify({"msg": "Account verified successfully! You can now log in."}), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    identifier = data.get('identifier')
    password = data.get('password')
    role = data.get('role')

    if not identifier or not password or not role:
        return jsonify({"msg": "Missing identifier, password, or role"}), 400

    user = None
    if role == 'student':
        user = User.find_by_student_id(identifier)
    elif role == 'advisor':
        user = User.find_by_email(identifier)
    
    if not user or not User.check_password(user['password'], password):
        return jsonify({"msg": "Bad identifier or password"}), 401
    
    if not user.get('is_verified'):
        return jsonify({"msg": "Account not verified. Please complete the verification step or register again."}), 403

    access_token = create_access_token(identity=str(user['_id']), additional_claims={"role": user['role']})
    return jsonify(access_token=access_token, role=user['role']), 200
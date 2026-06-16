from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import Certificate, User
from services.file_storage import save_certificate_file
from services.marks_calculator import calculate_potential_marks 
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
import os
from functools import wraps

students_bp = Blueprint('students', __name__)

def student_required():
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") != "student":
                return jsonify(msg="Students only!"), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

@students_bp.route('/profile', methods=['GET'])
@student_required()
def get_student_profile():
    user_id = get_jwt_identity()
    user = User.find_by_id(user_id)
    if not user:
        return jsonify({"msg": "Student profile not found"}), 404
    
    profile_data = {
        "student_id": user.get("student_id"),
        "name": user.get("username")
    }
    return jsonify(profile_data), 200


@students_bp.route('/certificates', methods=['POST'])
@student_required()
def upload_certificate():
    if 'certificate' not in request.files:
        return jsonify({"msg": "No certificate file provided"}), 400

    file = request.files['certificate']
    if file.filename == '':
        return jsonify({"msg": "No selected file"}), 400

    student_id = request.form.get('regno')
    student_name = request.form.get('name')
    school = request.form.get('school')
    branch = request.form.get('branch')
    academic_year = request.form.get('year')
    batch = request.form.get('batch')
    semester = request.form.get('sem')
    date = request.form.get('date')
    cert_type = request.form.get('type')
    venue = request.form.get('venue')
    participation = request.form.get('participation')
    category = request.form.get('category')
    description = request.form.get('description', '')

    required_fields = {
        'regno': student_id, 'name': student_name, 'school': school, 'branch': branch,
        'year': academic_year, 'batch': batch, 'sem': semester, 'date': date,
        'type': cert_type, 'venue': venue, 'participation': participation, 'category': category
    }
    for field, value in required_fields.items():
        if not value:
            return jsonify({"msg": f"Missing field: {field}"}), 400

    filename = save_certificate_file(file)
    if not filename:
        return jsonify({"msg": "Invalid file type or unable to save file"}), 400

    potential_marks = calculate_potential_marks(cert_type, category, participation)

    new_cert = Certificate(
        student_id=student_id,
        student_name=student_name,
        school=school,
        branch=branch,
        academic_year=academic_year,
        batch=batch,
        semester=semester,
        date=date,
        type=cert_type,
        venue=venue,
        participation=participation,
        category=f"{category} ({description})" if "Others" in category else category,
        filename=filename,
        potential_marks=potential_marks
    )
    cert_id = new_cert.save()

    return jsonify({"msg": "Certificate uploaded successfully!", "cert_id": cert_id, "filename": filename}), 201

@students_bp.route('/my-certificates', methods=['GET'])
@student_required()
def get_my_certificates():
    user_id = get_jwt_identity()
    user_doc = User.find_by_id(user_id)
    
    if not user_doc or user_doc.get('role') != 'student' or not user_doc.get('student_id'):
        return jsonify({"msg": "Student ID not found for this user."}), 403

    student_id_from_auth = user_doc['student_id']
    certs = Certificate.find_by_student_id(student_id_from_auth)
    
    for cert in certs:
        cert['id'] = str(cert['_id'])
        del cert['_id']
    
    return jsonify(certs), 200

@students_bp.route('/certificates/<cert_id>', methods=['DELETE'])
@student_required()
def delete_certificate(cert_id):
    user_id = get_jwt_identity()
    password = request.get_json().get('password')
    user = User.find_by_id(user_id)

    if not user or not User.check_password(user['password'], password):
        return jsonify({"msg": "Incorrect password"}), 401

    cert = Certificate.find_by_id(cert_id)
    if not cert or cert['student_id'] != user['student_id']:
        return jsonify({"msg": "Certificate not found or you do not have permission to delete it"}), 404

    # This line deletes the record from the database
    from models import certificates_collection
    certificates_collection.delete_one({'_id': ObjectId(cert_id)})
    
    # Optional: Delete the file from the server's file system
    try:
        from config import Config
        filepath = os.path.join(Config.UPLOAD_FOLDER, cert['filename'])
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Error deleting file from server: {e}")

    return jsonify({"msg": "Certificate deleted successfully"}), 200
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models import Certificate, User, certificates_collection 
from bson.objectid import ObjectId
from functools import wraps

advisor_bp = Blueprint('advisors', __name__)

def advisor_required():
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") != "advisor":
                return jsonify(msg="Advisors only!"), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

@advisor_bp.route('/all-certificates', methods=['GET'])
@advisor_required()
def get_all_certificates():
    try:
        all_certs = list(certificates_collection.find({})) 
        for cert in all_certs:
            cert['id'] = str(cert['_id'])
            cert['student'] = cert.get('student_name', 'N/A')
            del cert['_id']
        return jsonify(all_certs), 200
    except Exception as e:
        return jsonify(msg=f"An internal error occurred: {str(e)}"), 500

@advisor_bp.route('/review-certificate/<cert_id>', methods=['POST'])
@advisor_required()
def review_certificate_action(cert_id):
    data = request.get_json()
    status = data.get('status')
    allocated_marks = data.get('allocated_marks')
    if status not in ['Approved', 'Rejected']:
        return jsonify({"msg": "Invalid status"}), 400
    final_marks = int(allocated_marks) if status == 'Approved' else 0
    try:
        result = Certificate.update_status_and_marks(cert_id, status, final_marks)
        if result.modified_count == 1:
            return jsonify({"msg": f"Certificate {status.lower()} successfully"}), 200
        return jsonify({"msg": "Certificate not found or status is unchanged"}), 404
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@advisor_bp.route('/reject-all-by-id/<student_id>', methods=['POST'])
@advisor_required()
def reject_all_pending_by_id(student_id):
    try:
        result = certificates_collection.update_many(
            {"student_id": student_id, "status": "Pending"},
            {"$set": {"status": "Rejected", "allocated_marks": 0}}
        )
        if result.modified_count > 0:
            return jsonify({"msg": f"Rejected {result.modified_count} pending certificates for student {student_id}"}), 200
        else:
            return jsonify({"msg": "No pending certificates were found for this student."}), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

# --- *** NEW ENDPOINT FOR APPROVE ALL *** ---
@advisor_bp.route('/approve-all-by-id/<student_id>', methods=['POST'])
@advisor_required()
def approve_all_pending_by_id(student_id):
    try:
        # We need to update marks for each, so we can't use a simple update_many.
        # However, the frontend logic now prevents this from being called if there's nothing to approve.
        # This endpoint assumes there ARE pending certs.
        
        pending_certs = list(certificates_collection.find({"student_id": student_id, "status": "Pending"}))
        
        if not pending_certs:
             return jsonify({"msg": "No pending certificates were found to approve for this student."}), 200

        for cert in pending_certs:
            certificates_collection.update_one(
                {'_id': cert['_id']},
                {"$set": {"status": "Approved", "allocated_marks": cert.get("potential_marks", 0)}}
            )
        
        return jsonify({"msg": f"Approved {len(pending_certs)} pending certificates for student {student_id}"}), 200

    except Exception as e:
        return jsonify({"msg": str(e)}), 500
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from config import Config

# Connect to MongoDB (using PyMongo directly for collections)
client = MongoClient(Config.MONGO_URI)
db = client.get_database() # This will get the database from the URI

users_collection = db.users
certificates_collection = db.certificates

# ... (imports) ...

class User:
    def __init__(self, username, password, role, email=None, student_id=None):
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.role = role
        self.email = email
        self.student_id = student_id
        self.created_at = datetime.utcnow()
        self.is_verified = False # <<< ADD THIS NEW FIELD

    def save(self):
        user_data = {
            "username": self.username,
            "password": self.password_hash,
            "role": self.role,
            "created_at": self.created_at,
            "is_verified": self.is_verified # <<< ADD THIS TO THE SAVED DATA
        }
        if self.email:
            user_data["email"] = self.email
        if self.student_id:
            user_data["student_id"] = self.student_id
        
        # ... (rest of the save method is the same) ...
        # Ensure unique constraints
        if self.role == 'student':
            if users_collection.find_one({"role": "student", "student_id": self.student_id}):
                raise ValueError("Student ID already exists.")
        elif self.role == 'advisor':
            if users_collection.find_one({"role": "advisor", "email": self.email}):
                raise ValueError("Advisor email already exists.")
        
        result = users_collection.insert_one(user_data)
        return str(result.inserted_id)

    # ... (rest of the User class is the same) ...

    @staticmethod
    def find_by_username_and_role(username, role):
        return users_collection.find_one({"username": username, "role": role})

    @staticmethod
    def find_by_student_id(student_id):
        return users_collection.find_one({"role": "student", "student_id": student_id})

    @staticmethod
    def find_by_email(email):
        return users_collection.find_one({"role": "advisor", "email": email})
    
    @staticmethod
    def find_by_id(user_id):
        return users_collection.find_one({"_id": ObjectId(user_id)})

    @staticmethod
    def check_password(hashed_password, password):
        return check_password_hash(hashed_password, password)

class Certificate:
    def __init__(self, student_id, student_name, school, branch, academic_year, batch,
                 semester, date, type, venue, participation, category, filename,
                 potential_marks, submitted_date=None, status='Pending', allocated_marks=None):
        self.student_id = student_id
        self.student_name = student_name
        self.school = school
        self.branch = branch
        self.academic_year = academic_year
        self.batch = batch
        self.semester = semester
        self.date = date # Certificate date
        self.type = type
        self.venue = venue
        self.participation = participation
        self.category = category
        self.filename = filename # Stored filename
        self.potential_marks = potential_marks
        self.submitted_date = submitted_date if submitted_date else datetime.utcnow().isoformat()
        self.status = status # 'Pending', 'Approved', 'Rejected'
        self.allocated_marks = allocated_marks # Actual marks awarded by advisor

    def save(self):
        cert_data = {
            "student_id": self.student_id,
            "student_name": self.student_name,
            "school": self.school,
            "branch": self.branch,
            "academic_year": self.academic_year,
            "batch": self.batch,
            "semester": self.semester,
            "date": self.date,
            "type": self.type,
            "venue": self.venue,
            "participation": self.participation,
            "category": self.category,
            "filename": self.filename,
            "potential_marks": self.potential_marks,
            "submitted_date": self.submitted_date,
            "status": self.status,
            "allocated_marks": self.allocated_marks
        }
        result = certificates_collection.insert_one(cert_data)
        return str(result.inserted_id)

    @staticmethod
    def find_by_id(cert_id):
        return certificates_collection.find_one({"_id": ObjectId(cert_id)})

    @staticmethod
    def find_by_student_id(student_id):
        return list(certificates_collection.find({"student_id": student_id}))
    
    @staticmethod
    def find_all():
        return list(certificates_collection.find({}))

    @staticmethod
    def update_status_and_marks(cert_id, status, allocated_marks):
        return certificates_collection.update_one(
            {"_id": ObjectId(cert_id)},
            {"$set": {"status": status, "allocated_marks": allocated_marks}}
        )
    
    @staticmethod
    def update_many_by_student_id(student_id, status, allocated_marks=None):
        update_fields = {"status": status}
        if allocated_marks is not None:
             update_fields["allocated_marks"] = allocated_marks
        return certificates_collection.update_many(
            {"student_id": student_id, "status": "Pending"}, # Only update pending ones
            {"$set": update_fields}
        )

# Create unique indexes to prevent duplicate accounts
users_collection.create_index([("student_id", 1), ("role", 1)], unique=True, partialFilterExpression={"role": "student"})
users_collection.create_index([("email", 1), ("role", 1)], unique=True, partialFilterExpression={"role": "advisor"})
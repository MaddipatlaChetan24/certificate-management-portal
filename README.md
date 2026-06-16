# Certificate Management Portal

A web-based platform for students to submit certificates for extracurricular achievements and request grace marks, and for faculty advisors to review submissions, manage student records, and generate consolidated reports.

## Overview

Students upload proof of participation in technical competitions, sports, cultural events, Amma Service/Seva activities, or research publications. Each submission is tagged with academic details (school, branch, year, batch, semester) and routed to an advisor, who reviews the certificate, assigns grace marks, and approves or rejects it. Advisors can also browse all students, act in bulk, and export filtered reports as PDF, Excel, or CSV.

## Features

### Student
- Register and log in with a student ID, secured by email OTP verification
- Upload a certificate (PDF/JPG/PNG) via drag-and-drop, with school, branch, year, batch, semester, type, category, and prize/participation details
- Must read and acknowledge the grace marks policy before each upload
- Dashboard showing total certificates, accumulated grace marks, and approval count
- View certificate status (Pending / Approved / Rejected) and open the uploaded file
- Delete a certificate, confirmed by re-entering their password

### Advisor
- Register and log in with an advisor email, secured by email OTP verification
- Dashboard summary: total certificates, pending reviews, approvals, active students
- "All Students" view with per-student certificate/pending counts and bulk Approve All / Reject All actions
- "Approve Certificates" view to review individual submissions, adjust suggested grace marks, and approve or reject
- Search and filter certificates by student name, academic year, batch, school, branch, type, status, and semester
- "Reports" view summarizing approved certificates and grace marks per student, with a bar chart
- "Generate Report" view to export a filtered certificate list or cumulative student report as PDF, Excel, or CSV, with an institution letterhead

## Tech Stack

- **Backend:** Python, Flask, Flask-PyMongo / PyMongo, Flask-JWT-Extended, Flask-CORS, Flask-Mail, Werkzeug, python-dotenv
- **Database:** MongoDB
- **Frontend:** HTML, CSS, vanilla JavaScript (no framework)
- **Frontend libraries (CDN):** particles.js (background animation), Chart.js (grace marks chart), jsPDF + jspdf-autotable (client-side PDF generation)

## Project Structure

This layout is inferred from the files provided; adjust paths to match your actual backend code.

```
certificate-management-portal/
├── app.py                   # Flask application entry point (not included here)
├── requirements.txt
├── .env                     # Environment variables (not committed)
├── login.html               # Auth: student/advisor register, OTP verify, login
├── home.html                 # Student dashboard, upload form, certificate list
├── advisor.html              # Advisor dashboard, review queue, reports
└── static/certificates/      # Uploaded files, served at /certificates/<filename>
```

## Prerequisites

- Python 3.9+
- A MongoDB instance (local or MongoDB Atlas)
- An SMTP-capable email account for sending OTP codes (e.g. Gmail with an app password)

## Setup & Installation

1. Clone the repository and enter the project folder.

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root:
   ```
   MONGO_URI=mongodb://localhost:27017/certificate_portal
   JWT_SECRET_KEY=your-secret-key
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   ```

4. Run the backend:
   ```
   flask run
   ```
   The frontend expects the API at `http://127.0.0.1:5000` by default.

5. Open `login.html` in a browser, register an account, verify the OTP sent to your email, then log in. Students land on `home.html`; advisors land on `advisor.html`.

## API Reference

Endpoints below are inferred from the frontend's `fetch` calls. Confirm exact request/response shapes against your backend implementation.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register a new student or advisor account |
| POST | `/api/auth/verify` | Verify the OTP code sent to email |
| POST | `/api/auth/login` | Log in and receive a JWT access token |
| GET | `/api/students/profile` | Get the logged-in student's profile |
| GET | `/api/students/my-certificates` | List the logged-in student's certificates |
| POST | `/api/students/certificates` | Upload a new certificate (multipart form) |
| DELETE | `/api/students/certificates/<id>` | Delete a certificate (password required) |
| GET | `/api/advisors/all-certificates` | List all certificates across students |
| POST | `/api/advisors/review-certificate/<id>` | Approve or reject a certificate, with allocated marks |
| POST | `/api/advisors/approve-all-by-id/<student_id>` | Approve all pending certificates for a student |
| POST | `/api/advisors/reject-all-by-id/<student_id>` | Reject all pending certificates for a student |
| GET | `/certificates/<filename>` | Serve an uploaded certificate file |

## Grace Marks Policy

Summarized from the rules students must acknowledge before uploading:

- Grace marks aren't shown separately on the grade card.
- Total grace marks across all activities (sports, cultural, technical, Seva/NSS) are capped per semester.
- Grace marks don't factor into student ranking.
- Once awarded, an allocation can't be reopened on request.
- Grace marks apply to theory papers, except where used to cover a shortfall in viva-voce, projects, or practicals.
- Claims must be made in the semester the event concluded or results were declared.

## Before Deploying

- `API_URL` is hardcoded to `http://127.0.0.1:5000` in `login.html`, `home.html`, and `advisor.html` — update this for any non-local deployment.
- The institution logo used in generated PDF reports loads from an external `i.ibb.co` URL — consider self-hosting it for reliability.
- Certificate deletion requires a password in the UI; make sure the same check is enforced server-side.

## License

Add your preferred license here.

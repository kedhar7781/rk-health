# RK Health - API Documentation

The RK Health Flask backend exposes REST APIs for user authentication, appointment scheduling, medication tracking, notes logged by patients, and AI-powered health summaries.

## Core API Response Structure
Standard error responses return a JSON object with `error` and `message` strings:
```json
{
  "error": "Bad Request",
  "message": "Missing required fields"
}
```

---

## Authentication Endpoints (`/api/auth`)

### 1. Register Patient Account
- **Endpoint**: `POST /api/auth/register`
- **Payload**:
  ```json
  {
    "username": "patient1",
    "password": "securepassword",
    "email": "patient@rkhealth.com",
    "phone": "+15551234567"
  }
  ```
- **Responses**:
  - `201 Created`: User successfully registered.
  - `400 Bad Request`: Missing username or password.
  - `409 Conflict`: Username already exists.

### 2. Login Patient
- **Endpoint**: `POST /api/auth/login`
- **Payload**:
  ```json
  {
    "username": "patient1",
    "password": "securepassword"
  }
  ```
- **Responses**:
  - `200 OK`: Login successful. Sets cookie session `user_id` and returns user profile.
  - `401 Unauthorized`: Invalid credentials.

### 3. Check Session
- **Endpoint**: `GET /api/auth/me`
- **Responses**:
  - `200 OK`: Returns current user session payload or `null` if unauthenticated.

### 4. Logout Patient
- **Endpoint**: `POST /api/auth/logout`
- **Responses**:
  - `200 OK`: Clears user session.

---

## Appointments Endpoints (`/api/appointments`)
*Requires Authentication*

### 1. Get Scheduled Appointments
- **Endpoint**: `GET /api/appointments`
- **Query Parameters**:
  - `q` (optional): Filter appointments by patient name, doctor, or notes match.
  - `start_date` (optional): Filter appointments scheduled on or after `YYYY-MM-DD`.
  - `end_date` (optional): Filter appointments scheduled on or before `YYYY-MM-DD`.
- **Responses**:
  - `200 OK`: Returns list of appointment objects.

### 2. Create Appointment
- **Endpoint**: `POST /api/appointments`
- **Payload**:
  ```json
  {
    "patient_name": "John Doe",
    "doctor_name": "Dr. Sarah Jenkins (Cardiologist)",
    "appointment_date": "2026-07-02",
    "appointment_time": "10:30",
    "notes": "Cardiovascular ECG checkup.",
    "send_sms": true
  }
  ```
- **Responses**:
  - `201 Created`: Returns created appointment object, syncs with Google Sheets/Calendar, and triggers Twilio SMS confirmation.

### 3. Update Appointment
- **Endpoint**: `PUT /api/appointments/<int:appt_id>`
- **Payload**: Same as POST (excluding `send_sms`).
- **Responses**:
  - `200 OK`: Updates appointment and reflects changes on Sheets/Calendar.
  - `404 Not Found`: Appointment not found or unauthorized.

### 4. Cancel Appointment
- **Endpoint**: `DELETE /api/appointments/<int:appt_id>`
- **Responses**:
  - `200 OK`: Deletes appointment from database, Google Sheets, and Google Calendar.

---

## Medications Regimens (`/api/medications`)
*Requires Authentication*

### 1. Fetch Regimens
- **Endpoint**: `GET /api/medications`
- **Query Parameters**:
  - `status` (optional): Filter by `Active`, `Completed`, or `Paused`.
- **Responses**:
  - `200 OK`: Returns list of medications.

### 2. Add Medication Schedule
- **Endpoint**: `POST /api/medications`
- **Payload**:
  ```json
  {
    "medicine_name": "Lisinopril",
    "dosage": "10mg",
    "frequency": "Once daily (Morning)",
    "reminder_time": "08:00",
    "status": "Active",
    "phone_reminder": true
  }
  ```
- **Responses**:
  - `201 Created`: Regimen saved. Syncs with Google Sheets.

### 3. Update Medication Details
- **Endpoint**: `PUT /api/medications/<int:med_id>`
- **Payload**: Same as POST.
- **Responses**:
  - `200 OK`: Medication details updated.

### 4. Delete Medication Scheduler
- **Endpoint**: `DELETE /api/medications/<int:med_id>`
- **Responses**:
  - `200 OK`: Regimen deleted.

### 5. Trigger Manual SMS Tester Reminder
- **Endpoint**: `POST /api/medications/<int:med_id>/remind`
- **Responses**:
  - `200 OK`: Dispatches Twilio SMS reminder to target patient phone instantly.

---

## Health Notes Endpoints (`/api/notes`)
*Requires Authentication*

### 1. Fetch Health Logs
- **Endpoint**: `GET /api/notes`
- **Query Parameters**:
  - `q` (optional): Query term matching title or content.
- **Responses**:
  - `200 OK`: List of notes.

### 2. Create Note
- **Endpoint**: `POST /api/notes`
- **Payload**:
  ```json
  {
    "title": "Blood Pressure Daily Log",
    "content": "Averaging 130/85 this morning. Dry cough has subsided."
  }
  ```
- **Responses**:
  - `201 Created`: Note saved.

### 3. Update Note
- **Endpoint**: `PUT /api/notes/<int:note_id>`
- **Responses**:
  - `200 OK`: Note updated.

### 4. Delete Note
- **Endpoint**: `DELETE /api/notes/<int:note_id>`
- **Responses**:
  - `200 OK`: Note deleted.

---

## Diagnostic Summaries & Statistics (`/api/summary`)
*Requires Authentication*

### 1. Generate AI Health Report
- **Endpoint**: `GET /api/summary`
- **Responses**:
  - `200 OK`: Compiles all patient records and uses Llama/Grok/OpenAI to generate a structured patient clinical summary.
  ```json
  {
    "summary_markdown": "# Patient Visit Summary\n..."
  }
  ```

### 2. Fetch Dashboard Statistics
- **Endpoint**: `GET /api/summary/stats`
- **Responses**:
  - `200 OK`: Summarizes stats for cards and Chart.js graphs.
  ```json
  {
    "appointments": { "total": 2, "upcoming": 2 },
    "medications": { "total": 3, "active": 2, "completed": 1, "paused": 0, "frequencies": { "Once daily": 2 } },
    "notes": { "total": 2 }
  }
  ```

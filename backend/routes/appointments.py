from flask import Blueprint, request, jsonify, session
from backend.routes.auth import login_required
from backend.database import get_db_connection
from backend.services.google_service import GoogleService
from backend.services.twilio_service import TwilioService

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('', methods=['GET'])
@login_required
def get_appointments():
    user_id = session['user_id']
    query_param = request.args.get('q', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = "SELECT * FROM appointments WHERE user_id = ?"
    params = [user_id]
    
    if query_param:
        sql += " AND (patient_name LIKE ? OR doctor_name LIKE ? OR notes LIKE ?)"
        like_term = f"%{query_param}%"
        params.extend([like_term, like_term, like_term])
        
    if start_date:
        sql += " AND appointment_date >= ?"
        params.append(start_date)
        
    if end_date:
        sql += " AND appointment_date <= ?"
        params.append(end_date)
        
    sql += " ORDER BY appointment_date ASC, appointment_time ASC"
    
    try:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        appointments = [dict(row) for row in rows]
        return jsonify(appointments), 200
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        conn.close()

@appointments_bp.route('', methods=['POST'])
@login_required
def create_appointment():
    user_id = session['user_id']
    data = request.get_json() or {}
    
    patient_name = data.get('patient_name', '').strip()
    doctor_name = data.get('doctor_name', '').strip()
    appointment_date = data.get('appointment_date', '').strip()
    appointment_time = data.get('appointment_time', '').strip()
    notes = data.get('notes', '').strip()
    send_sms = data.get('send_sms', False)
    
    if not patient_name or not doctor_name or not appointment_date or not appointment_time:
        return jsonify({"error": "Bad Request", "message": "Missing required fields"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Insert locally
        cursor.execute(
            "INSERT INTO appointments (user_id, patient_name, doctor_name, appointment_date, appointment_time, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, patient_name, doctor_name, appointment_date, appointment_time, notes)
        )
        appt_id = cursor.lastrowid
        conn.commit()
        
        # Sync with Google Sheets & Calendar
        google_event_id = GoogleService.sync_appointment(
            appt_id, patient_name, doctor_name, appointment_date, appointment_time, notes
        )
        
        if google_event_id:
            cursor.execute(
                "UPDATE appointments SET google_event_id = ? WHERE id = ?",
                (google_event_id, appt_id)
            )
            conn.commit()
            
        # Twilio confirmation if checkmarked
        sms_status = None
        if send_sms:
            # Fetch user phone
            cursor.execute("SELECT phone FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            if user and user['phone']:
                sms_res = TwilioService.schedule_appointment_reminder(
                    patient_name, doctor_name, appointment_date, appointment_time, user['phone']
                )
                sms_status = sms_res.get("status")
            else:
                sms_status = "No user phone number configured."
                
        # Retrieve final saved object
        cursor.execute("SELECT * FROM appointments WHERE id = ?", (appt_id,))
        new_appt = dict(cursor.fetchone())
        new_appt['sms_status'] = sms_status
        
        return jsonify(new_appt), 201
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        conn.close()

@appointments_bp.route('/<int:appt_id>', methods=['PUT'])
@login_required
def update_appointment(appt_id):
    user_id = session['user_id']
    data = request.get_json() or {}
    
    patient_name = data.get('patient_name', '').strip()
    doctor_name = data.get('doctor_name', '').strip()
    appointment_date = data.get('appointment_date', '').strip()
    appointment_time = data.get('appointment_time', '').strip()
    notes = data.get('notes', '').strip()
    
    if not patient_name or not doctor_name or not appointment_date or not appointment_time:
        return jsonify({"error": "Bad Request", "message": "Missing required fields"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check ownership
        cursor.execute("SELECT id, google_event_id FROM appointments WHERE id = ? AND user_id = ?", (appt_id, user_id))
        appt = cursor.fetchone()
        if not appt:
            return jsonify({"error": "Not Found", "message": "Appointment not found or unauthorized"}), 404
            
        google_event_id = appt['google_event_id']
        
        # Update locally
        cursor.execute(
            "UPDATE appointments SET patient_name = ?, doctor_name = ?, appointment_date = ?, appointment_time = ?, notes = ? WHERE id = ?",
            (patient_name, doctor_name, appointment_date, appointment_time, notes, appt_id)
        )
        conn.commit()
        
        # Update Google Sheets & Calendar
        new_event_id = GoogleService.sync_appointment(
            appt_id, patient_name, doctor_name, appointment_date, appointment_time, notes, google_event_id
        )
        
        if new_event_id and new_event_id != google_event_id:
            cursor.execute("UPDATE appointments SET google_event_id = ? WHERE id = ?", (new_event_id, appt_id))
            conn.commit()
            
        # Get updated object
        cursor.execute("SELECT * FROM appointments WHERE id = ?", (appt_id,))
        updated_appt = dict(cursor.fetchone())
        
        return jsonify(updated_appt), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        conn.close()

@appointments_bp.route('/<int:appt_id>', methods=['DELETE'])
@login_required
def delete_appointment(appt_id):
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check ownership
        cursor.execute("SELECT id, google_event_id FROM appointments WHERE id = ? AND user_id = ?", (appt_id, user_id))
        appt = cursor.fetchone()
        if not appt:
            return jsonify({"error": "Not Found", "message": "Appointment not found or unauthorized"}), 404
            
        google_event_id = appt['google_event_id']
        
        # Delete locally
        cursor.execute("DELETE FROM appointments WHERE id = ?", (appt_id,))
        conn.commit()
        
        # Sync delete with Google Sheets & Calendar
        if google_event_id:
            GoogleService.delete_appointment(appt_id, google_event_id)
            
        return jsonify({"message": "Appointment deleted successfully"}), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        conn.close()

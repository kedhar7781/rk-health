from flask import Blueprint, request, jsonify, session
from backend.routes.auth import login_required
from backend.database import get_db_connection
from backend.services.google_service import GoogleService
from backend.services.twilio_service import TwilioService

medications_bp = Blueprint('medications', __name__)

@medications_bp.route('', methods=['GET'])
@login_required
def get_medications():
    user_id = session['user_id']
    status = request.args.get('status', '').strip()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = "SELECT * FROM medications WHERE user_id = ?"
    params = [user_id]
    
    if status:
        sql += " AND status = ?"
        params.append(status)
        
    sql += " ORDER BY reminder_time ASC"
    
    try:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        medications = [dict(row) for row in rows]
        return jsonify(medications), 200
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        conn.close()

@medications_bp.route('', methods=['POST'])
@login_required
def create_medication():
    user_id = session['user_id']
    data = request.get_json() or {}
    
    medicine_name = data.get('medicine_name', '').strip()
    dosage = data.get('dosage', '').strip()
    frequency = data.get('frequency', '').strip()
    reminder_time = data.get('reminder_time', '').strip()
    status = data.get('status', 'Active').strip()
    phone_reminder = 1 if data.get('phone_reminder', False) else 0
    
    if not medicine_name or not dosage or not frequency or not reminder_time:
        return jsonify({"error": "Bad Request", "message": "Missing required fields"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO medications (user_id, medicine_name, dosage, frequency, reminder_time, status, phone_reminder) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, medicine_name, dosage, frequency, reminder_time, status, phone_reminder)
        )
        med_id = cursor.lastrowid
        conn.commit()
        
        # Sync with Google Sheets
        GoogleService.sync_medication(
            med_id, medicine_name, dosage, frequency, reminder_time, status
        )
        
        # Twilio confirmation text if requested
        sms_status = None
        if phone_reminder == 1:
            cursor.execute("SELECT username, phone FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            if user and user['phone']:
                sms_res = TwilioService.send_sms(
                    user['phone'],
                    f"RK Health: Reminder created for {medicine_name} ({dosage}) at {reminder_time} daily. Health is wealth!"
                )
                sms_status = sms_res.get("status")
                
        cursor.execute("SELECT * FROM medications WHERE id = ?", (med_id,))
        new_med = dict(cursor.fetchone())
        new_med['sms_status'] = sms_status
        
        return jsonify(new_med), 201
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        conn.close()

@medications_bp.route('/<int:med_id>', methods=['PUT'])
@login_required
def update_medication(med_id):
    user_id = session['user_id']
    data = request.get_json() or {}
    
    medicine_name = data.get('medicine_name', '').strip()
    dosage = data.get('dosage', '').strip()
    frequency = data.get('frequency', '').strip()
    reminder_time = data.get('reminder_time', '').strip()
    status = data.get('status', 'Active').strip()
    phone_reminder = 1 if data.get('phone_reminder', False) else 0
    
    if not medicine_name or not dosage or not frequency or not reminder_time:
        return jsonify({"error": "Bad Request", "message": "Missing required fields"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check ownership
        cursor.execute("SELECT id FROM medications WHERE id = ? AND user_id = ?", (med_id, user_id))
        if not cursor.fetchone():
            return jsonify({"error": "Not Found", "message": "Medication not found or unauthorized"}), 404
            
        cursor.execute(
            "UPDATE medications SET medicine_name = ?, dosage = ?, frequency = ?, reminder_time = ?, status = ?, phone_reminder = ? WHERE id = ?",
            (medicine_name, dosage, frequency, reminder_time, status, phone_reminder, med_id)
        )
        conn.commit()
        
        # Sync with Google Sheets
        GoogleService.sync_medication(
            med_id, medicine_name, dosage, frequency, reminder_time, status
        )
        
        cursor.execute("SELECT * FROM medications WHERE id = ?", (med_id,))
        updated_med = dict(cursor.fetchone())
        
        return jsonify(updated_med), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        conn.close()

@medications_bp.route('/<int:med_id>', methods=['DELETE'])
@login_required
def delete_medication(med_id):
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check ownership
        cursor.execute("SELECT id FROM medications WHERE id = ? AND user_id = ?", (med_id, user_id))
        if not cursor.fetchone():
            return jsonify({"error": "Not Found", "message": "Medication not found or unauthorized"}), 404
            
        cursor.execute("DELETE FROM medications WHERE id = ?", (med_id,))
        conn.commit()
        
        # Sync delete with Google Sheets
        GoogleService.delete_medication(med_id)
        
        return jsonify({"message": "Medication deleted successfully"}), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        conn.close()

@medications_bp.route('/<int:med_id>/remind', methods=['POST'])
@login_required
def trigger_manual_reminder(med_id):
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check ownership & fetch med data
        cursor.execute("SELECT * FROM medications WHERE id = ? AND user_id = ?", (med_id, user_id))
        med = cursor.fetchone()
        if not med:
            return jsonify({"error": "Not Found", "message": "Medication not found or unauthorized"}), 404
            
        # Fetch user
        cursor.execute("SELECT username, phone FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user or not user['phone']:
            return jsonify({"error": "Bad Request", "message": "You must configure a valid phone number in your profile/settings to receive reminders."}), 400
            
        # Trigger Twilio SMS
        sms_res = TwilioService.schedule_reminder(
            user['username'], med['medicine_name'], med['dosage'], med['reminder_time'], user['phone']
        )
        
        return jsonify(sms_res), 200
        
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        conn.close()

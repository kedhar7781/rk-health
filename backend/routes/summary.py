from flask import Blueprint, jsonify, session
from backend.routes.auth import login_required
from backend.database import get_db_connection
from backend.services.ai_service import AIService

summary_bp = Blueprint('summary', __name__)

@summary_bp.route('', methods=['GET'])
@login_required
def get_ai_summary():
    user_id = session['user_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Fetch all data for this patient
        cursor.execute("SELECT appointment_date, appointment_time, doctor_name, notes FROM appointments WHERE user_id = ? ORDER BY appointment_date ASC", (user_id,))
        appointments = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("SELECT medicine_name, dosage, frequency, reminder_time, status FROM medications WHERE user_id = ?", (user_id,))
        medications = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("SELECT title, content FROM health_notes WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        notes = [dict(row) for row in cursor.fetchall()]
        
        # Call AI generation service
        ai_markdown = AIService.generate_ai_summary(appointments, medications, notes)
        
        return jsonify({
            "summary_markdown": ai_markdown
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        conn.close()

@summary_bp.route('/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    user_id = session['user_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Appointments stats
        cursor.execute("SELECT COUNT(*) FROM appointments WHERE user_id = ?", (user_id,))
        total_appointments = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM appointments WHERE user_id = ? AND appointment_date >= date('now')", (user_id,))
        upcoming_appointments = cursor.fetchone()[0]
        
        # Medications stats
        cursor.execute("SELECT COUNT(*) FROM medications WHERE user_id = ?", (user_id,))
        total_medications = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM medications WHERE user_id = ? AND status = 'Active'", (user_id,))
        active_medications = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM medications WHERE user_id = ? AND status = 'Completed'", (user_id,))
        completed_medications = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM medications WHERE user_id = ? AND status = 'Paused'", (user_id,))
        paused_medications = cursor.fetchone()[0]
        
        # Notes stats
        cursor.execute("SELECT COUNT(*) FROM health_notes WHERE user_id = ?", (user_id,))
        total_notes = cursor.fetchone()[0]
        
        # Get weekly medication distribution or frequency breakdown for charts
        cursor.execute("SELECT frequency, COUNT(*) as count FROM medications WHERE user_id = ? GROUP BY frequency", (user_id,))
        freq_rows = cursor.fetchall()
        medication_frequencies = {row['frequency']: row['count'] for row in freq_rows}
        
        return jsonify({
            "appointments": {
                "total": total_appointments,
                "upcoming": upcoming_appointments
            },
            "medications": {
                "total": total_medications,
                "active": active_medications,
                "completed": completed_medications,
                "paused": paused_medications,
                "frequencies": medication_frequencies
            },
            "notes": {
                "total": total_notes
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        conn.close()

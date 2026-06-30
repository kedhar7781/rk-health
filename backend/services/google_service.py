import requests
import logging
from backend.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleService:
    @staticmethod
    def _send_request(payload):
        url = Config.GOOGLE_APPS_SCRIPT_URL
        if not url:
            logger.warning("Google Apps Script URL is not configured. Google Sheets & Calendar integration is disabled.")
            return {"status": "disabled", "message": "Google Integration not configured."}
            
        try:
            # We send POST request containing action and data
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Google Apps Script returned status code {response.status_code}: {response.text}")
                return {"status": "error", "message": f"Apps Script error: {response.status_code}"}
        except Exception as e:
            logger.exception("Failed to connect to Google Apps Script Web App")
            return {"status": "error", "message": str(e)}

    @classmethod
    def sync_appointment(cls, appt_id, patient_name, doctor_name, appt_date, appt_time, notes, google_event_id=None):
        """
        Synchronizes an appointment to Google Sheets and creates or updates a Google Calendar event.
        Returns the calendar event ID if successful.
        """
        payload = {
            "action": "sync_appointment",
            "data": {
                "id": appt_id,
                "patient_name": patient_name,
                "doctor_name": doctor_name,
                "appointment_date": appt_date,
                "appointment_time": appt_time,
                "notes": notes or "",
                "google_event_id": google_event_id
            }
        }
        
        result = cls._send_request(payload)
        if result.get("status") == "success":
            logger.info(f"Successfully synced appointment {appt_id} with Google Sheets/Calendar.")
            return result.get("google_event_id")
        elif result.get("status") == "disabled":
            # Fallback for local sandbox testing
            import uuid
            return google_event_id or f"mock-cal-event-{uuid.uuid4().hex[:12]}"
        return google_event_id

    @classmethod
    def delete_appointment(cls, appt_id, google_event_id):
        """
        Deletes an appointment from Google Sheets and removes its associated Google Calendar event.
        """
        if not google_event_id:
            logger.warning(f"No Google Event ID provided for appointment {appt_id}. Skipping Google sync delete.")
            return False
            
        payload = {
            "action": "delete_appointment",
            "data": {
                "id": appt_id,
                "google_event_id": google_event_id
            }
        }
        
        result = cls._send_request(payload)
        return result.get("status") == "success"

    @classmethod
    def sync_medication(cls, med_id, medicine_name, dosage, frequency, reminder_time, status):
        """
        Synchronizes medication to Google Sheets.
        """
        payload = {
            "action": "sync_medication",
            "data": {
                "id": med_id,
                "medicine_name": medicine_name,
                "dosage": dosage,
                "frequency": frequency,
                "reminder_time": reminder_time,
                "status": status
            }
        }
        
        result = cls._send_request(payload)
        return result.get("status") in ["success", "disabled"]

    @classmethod
    def delete_medication(cls, med_id):
        """
        Removes medication from Google Sheets.
        """
        payload = {
            "action": "delete_medication",
            "data": {
                "id": med_id
            }
        }
        
        result = cls._send_request(payload)
        return result.get("status") in ["success", "disabled"]

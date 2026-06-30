import logging
import re
from twilio.rest import Client
from backend.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwilioService:
    @staticmethod
    def validate_phone_number(phone_number):
        """
        Validates E.164 phone number format.
        Basic regex check: starts with + followed by 10 to 15 digits.
        """
        if not phone_number:
            return False
            
        cleaned = re.sub(r'[\s\-\(\)]', '', phone_number)
        pattern = re.compile(r'^\+[1-9]\d{1,14}$')
        return bool(pattern.match(cleaned))

    @classmethod
    def send_sms(cls, to_phone, message_body):
        """
        Sends an SMS using Twilio.
        If Twilio credentials are not set, logs the message contents locally.
        """
        # Clean phone format
        to_phone_cleaned = re.sub(r'[\s\-\(\)]', '', to_phone)
        if not to_phone_cleaned.startswith('+'):
            # Default to US country code +1 if not provided, just as a helper
            to_phone_cleaned = '+1' + to_phone_cleaned
            
        if not cls.validate_phone_number(to_phone_cleaned):
            logger.error(f"Invalid phone number format: {to_phone}. Must match E.164 (e.g. +1234567890).")
            return {"status": "error", "message": "Invalid phone number format. Must start with country code (e.g. +1)."}

        account_sid = Config.TWILIO_ACCOUNT_SID
        auth_token = Config.TWILIO_AUTH_TOKEN
        from_phone = Config.TWILIO_PHONE_NUMBER

        if not account_sid or not auth_token or not from_phone:
            logger.warning("Twilio credentials not configured. Printing SMS output to console logs.")
            print(f"\n[MOCK SMS] To: {to_phone_cleaned}\n[MOCK SMS] Message: {message_body}\n")
            return {"status": "mocked", "message": "SMS logged to server console (Twilio not configured)."}

        try:
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                body=message_body,
                from_=from_phone,
                to=to_phone_cleaned
            )
            logger.info(f"SMS sent successfully to {to_phone_cleaned}. Message SID: {message.sid}")
            return {"status": "success", "sid": message.sid}
        except Exception as e:
            logger.exception(f"Failed to send SMS via Twilio to {to_phone_cleaned}")
            return {"status": "error", "message": str(e)}
            
    @classmethod
    def schedule_reminder(cls, patient_name, medication_name, dosage, time_str, phone):
        """
        Helper method to format and trigger a medication SMS reminder immediately.
        """
        msg = f"RK Health Reminder: Hi {patient_name}, it's time to take your {medication_name} ({dosage}) scheduled for {time_str}."
        return cls.send_sms(phone, msg)
        
    @classmethod
    def schedule_appointment_reminder(cls, patient_name, doctor_name, date_str, time_str, phone):
        """
        Helper method to format and trigger an appointment SMS reminder immediately.
        """
        msg = f"RK Health Appointment: Hi {patient_name}, you have an appointment with {doctor_name} scheduled on {date_str} at {time_str}."
        return cls.send_sms(phone, msg)

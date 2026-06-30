import sqlite3
import os
from werkzeug.security import generate_password_hash
from backend.config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Appointments Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            patient_name TEXT NOT NULL,
            doctor_name TEXT NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            notes TEXT,
            google_event_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # 3. Medications Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            medicine_name TEXT NOT NULL,
            dosage TEXT NOT NULL,
            frequency TEXT NOT NULL,
            reminder_time TEXT NOT NULL,
            status TEXT DEFAULT 'Active',
            phone_reminder INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # 4. Health Notes Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    
    # Seed sample dataset if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Create a sample user
        # Password will be: admin123
        hashed_password = generate_password_hash("admin123")
        cursor.execute(
            "INSERT INTO users (username, password_hash, email, phone) VALUES (?, ?, ?, ?)",
            ("admin", hashed_password, "patient@rkhealth.com", "+15555555555")
        )
        user_id = cursor.lastrowid
        
        # Add sample appointments
        cursor.execute(
            "INSERT INTO appointments (user_id, patient_name, doctor_name, appointment_date, appointment_time, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, "John Doe", "Dr. Sarah Jenkins (Cardiologist)", "2026-07-02", "10:30", "Bi-annual cardiovascular checkup and ECG reading review.")
        )
        cursor.execute(
            "INSERT INTO appointments (user_id, patient_name, doctor_name, appointment_date, appointment_time, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, "John Doe", "Dr. Alan Mercer (Dermatologist)", "2026-07-15", "14:15", "Follow up on eczema rash treatment progress.")
        )
        
        # Add sample medications
        cursor.execute(
            "INSERT INTO medications (user_id, medicine_name, dosage, frequency, reminder_time, status, phone_reminder) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, "Lisinopril", "10mg", "Once daily (Morning)", "08:00", "Active", 1)
        )
        cursor.execute(
            "INSERT INTO medications (user_id, medicine_name, dosage, frequency, reminder_time, status, phone_reminder) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, "Atorvastatin", "20mg", "Once daily (Night)", "21:30", "Active", 1)
        )
        cursor.execute(
            "INSERT INTO medications (user_id, medicine_name, dosage, frequency, reminder_time, status, phone_reminder) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, "Amoxicillin", "500mg", "Three times daily", "13:00", "Completed", 0)
        )
        
        # Add sample health notes
        cursor.execute(
            "INSERT INTO health_notes (user_id, title, content) VALUES (?, ?, ?)",
            (user_id, "Cardio Visit Notes", "Felt occasional palpitations last week. Dr. Jenkins suggested monitoring caffeine intake and tracking blood pressure twice daily. Blood pressure currently averages 130/85.")
        )
        cursor.execute(
            "INSERT INTO health_notes (user_id, title, content) VALUES (?, ?, ?)",
            (user_id, "Medication Side Effects", "Lisinopril causes a slight dry cough in the first hour after taking it, but it subsides quickly. No dizziness reported.")
        )
        
        conn.commit()
        
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")

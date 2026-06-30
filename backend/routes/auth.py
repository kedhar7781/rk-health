from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from backend.database import get_db_connection

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()

    if not username or not password:
        return jsonify({"error": "Bad Request", "message": "Username and password are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if username exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return jsonify({"error": "Conflict", "message": "Username is already taken"}), 409

        # Insert user
        password_hash = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash, email, phone) VALUES (?, ?, ?, ?)",
            (username, password_hash, email, phone)
        )
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        conn.close()

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({"error": "Bad Request", "message": "Username and password are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, username, password_hash, email, phone FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return jsonify({
                "message": "Login successful",
                "user": {
                    "id": user['id'],
                    "username": user['username'],
                    "email": user['email'],
                    "phone": user['phone']
                }
            }), 200
        else:
            return jsonify({"error": "Unauthorized", "message": "Invalid username or password"}), 401
    finally:
        conn.close()

@auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    if 'user_id' not in session:
        return jsonify({"user": None}), 200
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, username, email, phone FROM users WHERE id = ?", (session['user_id'],))
        user = cursor.fetchone()
        if user:
            return jsonify({
                "user": {
                    "id": user['id'],
                    "username": user['username'],
                    "email": user['email'],
                    "phone": user['phone']
                }
            }), 200
        return jsonify({"user": None}), 200
    finally:
        conn.close()

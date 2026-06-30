from flask import Blueprint, request, jsonify, session
from backend.routes.auth import login_required
from backend.database import get_db_connection

notes_bp = Blueprint('notes', __name__)

@notes_bp.route('', methods=['GET'])
@login_required
def get_notes():
    user_id = session['user_id']
    query_param = request.args.get('q', '').strip()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = "SELECT * FROM health_notes WHERE user_id = ?"
    params = [user_id]
    
    if query_param:
        sql += " AND (title LIKE ? OR content LIKE ?)"
        like_term = f"%{query_param}%"
        params.extend([like_term, like_term])
        
    sql += " ORDER BY created_at DESC"
    
    try:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        notes = [dict(row) for row in rows]
        return jsonify(notes), 200
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        conn.close()

@notes_bp.route('', methods=['POST'])
@login_required
def create_note():
    user_id = session['user_id']
    data = request.get_json() or {}
    
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    
    if not title or not content:
        return jsonify({"error": "Bad Request", "message": "Missing title or content"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO health_notes (user_id, title, content) VALUES (?, ?, ?)",
            (user_id, title, content)
        )
        note_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute("SELECT * FROM health_notes WHERE id = ?", (note_id,))
        new_note = dict(cursor.fetchone())
        return jsonify(new_note), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        conn.close()

@notes_bp.route('/<int:note_id>', methods=['PUT'])
@login_required
def update_note(note_id):
    user_id = session['user_id']
    data = request.get_json() or {}
    
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    
    if not title or not content:
        return jsonify({"error": "Bad Request", "message": "Missing title or content"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM health_notes WHERE id = ? AND user_id = ?", (note_id, user_id))
        if not cursor.fetchone():
            return jsonify({"error": "Not Found", "message": "Note not found or unauthorized"}), 404
            
        cursor.execute(
            "UPDATE health_notes SET title = ?, content = ? WHERE id = ?",
            (title, content, note_id)
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM health_notes WHERE id = ?", (note_id,))
        updated_note = dict(cursor.fetchone())
        return jsonify(updated_note), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        conn.close()

@notes_bp.route('/<int:note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM health_notes WHERE id = ? AND user_id = ?", (note_id, user_id))
        if not cursor.fetchone():
            return jsonify({"error": "Not Found", "message": "Note not found or unauthorized"}), 404
            
        cursor.execute("DELETE FROM health_notes WHERE id = ?", (note_id,))
        conn.commit()
        return jsonify({"message": "Note deleted successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        conn.close()

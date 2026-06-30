import os
import sys
from flask import Flask, send_from_directory
from flask_cors import CORS
from backend.config import Config
from backend.database import init_db
from backend.routes.auth import auth_bp
from backend.routes.appointments import appointments_bp
from backend.routes.medications import medications_bp
from backend.routes.notes import notes_bp
from backend.routes.summary import summary_bp

# Add parent directory to path so imports work correctly when running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set frontend directory path relative to this app file
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
app.config.from_object(Config)

# Enable CORS for local cross-origin development (like running frontend and backend separately)
CORS(app, supports_credentials=True)

# Register API blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(appointments_bp, url_prefix='/api/appointments')
app.register_blueprint(medications_bp, url_prefix='/api/medications')
app.register_blueprint(notes_bp, url_prefix='/api/notes')
app.register_blueprint(summary_bp, url_prefix='/api/summary')

# Routes to serve frontend pages
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/login')
def login():
    return app.send_static_file('login.html')

@app.route('/register')
def register():
    return app.send_static_file('register.html')

# Catch-all route to serve static files correctly
@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return app.send_static_file('index.html')

# Error handling
@app.errorhandler(404)
def page_not_found(e):
    return app.send_static_file('index.html')

@app.errorhandler(500)
def server_error(e):
    return {"error": "Internal Server Error", "message": "An unexpected error occurred on the server."}, 500

# Initialize Database on startup
with app.app_context():
    init_db()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rk_health.db')

# Simple manual environment loader for .env file if it exists
env_path = BASE_DIR / '.env'
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, val = line.split('=', 1)
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'rk_health_secret_key_129837198273')
    DATABASE_PATH = os.getenv('DATABASE_PATH', DB_PATH)
    
    # Google Integrations
    GOOGLE_APPS_SCRIPT_URL = os.getenv('GOOGLE_APPS_SCRIPT_URL', '')
    
    # Twilio API Configuration
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '')
    
    # OpenAI/Grok/Llama Compatible AI Configuration
    AI_API_KEY = os.getenv('AI_API_KEY', '')
    # Custom API base if using custom models like Grok or Llama host
    AI_API_BASE = os.getenv('AI_API_BASE', 'https://api.openai.com/v1')
    AI_MODEL = os.getenv('AI_MODEL', 'gpt-3.5-turbo')

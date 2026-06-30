import os
import tempfile
import pytest
import sys

# Ensure backend package can be imported from tests
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app import app as flask_app
from backend.config import Config
from backend.database import init_db

@pytest.fixture
def app():
    # Setup temporary db file
    db_fd, temp_db_path = tempfile.mkstemp()
    
    # Configure app settings for testing
    flask_app.config.update({
        'TESTING': True,
        'DATABASE_PATH': temp_db_path,
        'SECRET_KEY': 'test_secret_keys'
    })
    
    # Overwrite Config parameters
    Config.DATABASE_PATH = temp_db_path
    
    with flask_app.app_context():
        init_db()
        
    yield flask_app
    
    # Teardown
    os.close(db_fd)
    try:
        os.unlink(temp_db_path)
    except OSError:
        pass

@pytest.fixture
def client(app):
    return app.test_client()

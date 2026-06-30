import json

def test_register(client):
    # Test valid register
    response = client.post('/api/auth/register', json={
        'username': 'testpatient',
        'email': 'test@patient.com',
        'phone': '+15551234567',
        'password': 'password123'
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert "User registered successfully" in data['message']

    # Test duplicate username register
    response = client.post('/api/auth/register', json={
        'username': 'testpatient',
        'email': 'test2@patient.com',
        'phone': '+15551234567',
        'password': 'password123'
    })
    assert response.status_code == 409

def test_login_and_logout(client):
    # Register first
    client.post('/api/auth/register', json={
        'username': 'patientone',
        'email': 'p1@patient.com',
        'phone': '+15551111111',
        'password': 'mypassword'
    })

    # Test invalid login credentials
    response = client.post('/api/auth/login', json={
        'username': 'patientone',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401

    # Test valid login
    response = client.post('/api/auth/login', json={
        'username': 'patientone',
        'password': 'mypassword'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['user']['username'] == 'patientone'

    # Test /me session validation
    response = client.get('/api/auth/me')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['user']['username'] == 'patientone'

    # Test logout
    response = client.post('/api/auth/logout')
    assert response.status_code == 200

    # Test /me after logout
    response = client.get('/api/auth/me')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['user'] is None

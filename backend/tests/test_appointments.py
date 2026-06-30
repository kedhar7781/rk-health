import json

def login_helper(client):
    client.post('/api/auth/register', json={
        'username': 'apptuser',
        'email': 'appt@test.com',
        'phone': '+15552223333',
        'password': 'password123'
    })
    client.post('/api/auth/login', json={
        'username': 'apptuser',
        'password': 'password123'
    })

def test_appointment_crud(client):
    login_helper(client)
    
    # 1. Create Appointment
    response = client.post('/api/appointments', json={
        'patient_name': 'John Doe',
        'doctor_name': 'Dr. Sarah',
        'appointment_date': '2026-07-05',
        'appointment_time': '10:00',
        'notes': 'Cardiovascular consult',
        'send_sms': False
    })
    assert response.status_code == 201
    appt = json.loads(response.data)
    assert appt['patient_name'] == 'John Doe'
    appt_id = appt['id']
    
    # 2. Get Appointments (with query search)
    response = client.get('/api/appointments?q=Cardio')
    assert response.status_code == 200
    appts = json.loads(response.data)
    assert len(appts) == 1
    assert appts[0]['id'] == appt_id
    
    # Get with mismatching search
    response = client.get('/api/appointments?q=Dermatology')
    assert response.status_code == 200
    appts = json.loads(response.data)
    assert len(appts) == 0
    
    # 3. Update Appointment
    response = client.put(f'/api/appointments/{appt_id}', json={
        'patient_name': 'John Doe',
        'doctor_name': 'Dr. Sarah Jenkins',
        'appointment_date': '2026-07-06',
        'appointment_time': '11:00',
        'notes': 'Follow up cardiology checkup'
    })
    assert response.status_code == 200
    updated = json.loads(response.data)
    assert updated['doctor_name'] == 'Dr. Sarah Jenkins'
    assert updated['appointment_date'] == '2026-07-06'
    
    # 4. Delete Appointment
    response = client.delete(f'/api/appointments/{appt_id}')
    assert response.status_code == 200
    
    # Get after delete
    response = client.get('/api/appointments')
    assert response.status_code == 200
    appts = json.loads(response.data)
    assert len(appts) == 0

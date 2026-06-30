import json

def login_helper(client):
    client.post('/api/auth/register', json={
        'username': 'meduser',
        'email': 'med@test.com',
        'phone': '+15559998888',
        'password': 'password123'
    })
    client.post('/api/auth/login', json={
        'username': 'meduser',
        'password': 'password123'
    })

def test_medication_crud_and_remind(client):
    login_helper(client)
    
    # 1. Create Medication Regimen
    response = client.post('/api/medications', json={
        'medicine_name': 'Lisinopril',
        'dosage': '10mg',
        'frequency': 'Once daily',
        'reminder_time': '08:00',
        'status': 'Active',
        'phone_reminder': True
    })
    assert response.status_code == 201
    med = json.loads(response.data)
    assert med['medicine_name'] == 'Lisinopril'
    med_id = med['id']
    
    # 2. Get medications
    response = client.get('/api/medications?status=Active')
    assert response.status_code == 200
    meds = json.loads(response.data)
    assert len(meds) == 1
    assert meds[0]['id'] == med_id
    
    # Get with Completed status (should be empty)
    response = client.get('/api/medications?status=Completed')
    assert response.status_code == 200
    meds = json.loads(response.data)
    assert len(meds) == 0
    
    # 3. Test Manual Remind Trigger
    response = client.post(f'/api/medications/{med_id}/remind')
    assert response.status_code == 200
    remind_res = json.loads(response.data)
    assert remind_res['status'] in ['success', 'mocked']
    
    # 4. Update Medication
    response = client.put(f'/api/medications/{med_id}', json={
        'medicine_name': 'Lisinopril',
        'dosage': '20mg',
        'frequency': 'Once daily',
        'reminder_time': '09:00',
        'status': 'Completed',
        'phone_reminder': False
    })
    assert response.status_code == 200
    updated = json.loads(response.data)
    assert updated['dosage'] == '20mg'
    assert updated['status'] == 'Completed'
    
    # 5. Delete Medication
    response = client.delete(f'/api/medications/{med_id}')
    assert response.status_code == 200
    
    # Verify deletion
    response = client.get('/api/medications')
    assert response.status_code == 200
    meds = json.loads(response.data)
    assert len(meds) == 0

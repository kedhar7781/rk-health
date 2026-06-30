import json

def login_helper(client):
    client.post('/api/auth/register', json={
        'username': 'notesuser',
        'email': 'notes@test.com',
        'phone': '+15554445555',
        'password': 'password123'
    })
    client.post('/api/auth/login', json={
        'username': 'notesuser',
        'password': 'password123'
    })

def test_notes_crud(client):
    login_helper(client)
    
    # 1. Create Note
    response = client.post('/api/notes', json={
        'title': 'Cardio Checkup',
        'content': 'Doctor Jenkins advised limiting coffee due to palpitations.'
    })
    assert response.status_code == 201
    note = json.loads(response.data)
    assert note['title'] == 'Cardio Checkup'
    note_id = note['id']
    
    # 2. Get Notes with Search
    response = client.get('/api/notes?q=coffee')
    assert response.status_code == 200
    notes = json.loads(response.data)
    assert len(notes) == 1
    assert notes[0]['id'] == note_id
    
    # Search not matching
    response = client.get('/api/notes?q=rash')
    assert response.status_code == 200
    notes = json.loads(response.data)
    assert len(notes) == 0
    
    # 3. Update Note
    response = client.put(f'/api/notes/{note_id}', json={
        'title': 'Cardio Checkup Modified',
        'content': 'Doctor Jenkins advised limiting coffee. BP checks daily.'
    })
    assert response.status_code == 200
    updated = json.loads(response.data)
    assert updated['title'] == 'Cardio Checkup Modified'
    assert 'BP checks daily' in updated['content']
    
    # 4. Delete Note
    response = client.delete(f'/api/notes/{note_id}')
    assert response.status_code == 200
    
    # Verify deletion
    response = client.get('/api/notes')
    assert response.status_code == 200
    notes = json.loads(response.data)
    assert len(notes) == 0

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_create_valid_solicitude(client):
    payload = {
        "external_id": "REQ-12345",
        "request_type": "soporte técnico",
        "requester_name": "Test User",
        "email": "test@example.com",
        "description": "Need help with login",
        "priority": "alta"
    }
    response = client.post("/solicitudes", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["external_id"] == payload["external_id"]
    assert data["status"] == "recibida"
    assert "id" in data

def test_create_duplicate_solicitude(client):
    payload = {
        "external_id": "REQ-UNIQUE",
        "request_type": "académica",
        "requester_name": "Test",
        "email": "test@test.com",
        "description": "some large description",
        "priority": "media"
    }
    # First creation should succeed
    client.post("/solicitudes", json=payload)
    
    # Second creation with same external_id should fail with 409 Conflict
    response = client.post("/solicitudes", json=payload)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]

def test_invalid_data_rejection(client):
    payload = {
        "external_id": "REQ-BAD",
        # Missing required fields like email, description
        "priority": "alta"
    }
    response = client.post("/solicitudes", json=payload)
    assert response.status_code == 422 # Unprocessable Entity validation error

def test_update_status(client):
    # 1. Create it
    payload = {
        "external_id": "REQ-UPDATE",
        "request_type": "académica",
        "requester_name": "Test",
        "email": "test@test.com",
        "description": "some description",
        "priority": "media"
    }
    create_response = client.post("/solicitudes", json=payload)
    solicitude_id = create_response.json()["id"]

    # 2. Update it
    update_payload = {"status": "en proceso"}
    update_response = client.patch(f"/solicitudes/{solicitude_id}/estado", json=update_payload)
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "en proceso"

def test_get_nonexistent_solicitude(client):
    response = client.get("/solicitudes/99999")
    assert response.status_code == 404

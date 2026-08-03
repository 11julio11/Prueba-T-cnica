import uuid

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker

from backend.app.infrastructure.database.connection import Base, get_db
from backend.app.main import app

# Create an in-memory SQLite database
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=pool.StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

client = TestClient(app)
def create_request_helper():
    response = client.post(
        "/api/v1/requests",
        json={
            "external_id": str(uuid.uuid4()),
            "type": "technical_support",
            "requester_name": "John Doe",
            "email": "john.doe@example.com",
            "description": "I need help with my laptop.",
            "priority": "high"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "technical_support"
    assert data["requester_name"] == "John Doe"
    assert "external_id" in data

    return data["external_id"]

def test_create_request():
    create_request_helper()

def test_list_requests():
    # Insert one to make sure list isn't empty
    create_request_helper()

    response = client.get("/api/v1/requests")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) >= 1

def test_get_request():
    req_id = create_request_helper()
    response = client.get(f"/api/v1/requests/{req_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["external_id"] == req_id

def test_update_request_status():
    req_id = create_request_helper()
    response = client.patch(
        f"/api/v1/requests/{req_id}/status",
        json={
            "status": "in_progress",
            "justification": "Starting to work on it"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"

"""
Unit tests for health endpoints.
Verifies availability and DB readiness checks without a real DB.
"""
import os
from unittest.mock import patch

# Inject required env vars before importing anything from app
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")

from fastapi.testclient import TestClient



def test_health_returns_ok():
    with patch("backend.app.config.Settings.model_post_init", return_value=None):
        from backend.app.main import app
        client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"

def test_health_contains_service_name():
    from backend.app.main import app
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/health")
    assert "service" in response.json()



def test_ready_when_db_connected():
    from backend.app.main import app
    client = TestClient(app, raise_server_exceptions=False)

    with patch("backend.app.api.v1.routers.health.check_db_connection", return_value=True):
        response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"

def test_not_ready_when_db_unavailable():
    from backend.app.main import app
    client = TestClient(app, raise_server_exceptions=False)

    with patch("backend.app.api.v1.routers.health.check_db_connection", return_value=False):
        response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"

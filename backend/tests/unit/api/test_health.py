"""
Unit tests for health endpoints.
Verifies availability and DB readiness checks without a real DB.
"""
import os
from unittest.mock import patch

# Inject required env vars before importing anything from app
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")

from fastapi.testclient import TestClient  # noqa: E402


class TestHealthEndpoint:

    def test_health_returns_ok(self):
        with patch("app.config.Settings.model_post_init", return_value=None):
            from app.main import app
            client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"

    def test_health_contains_service_name(self):
        from app.main import app
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/health")
        assert "service" in response.json()


class TestHealthReadyEndpoint:

    def test_ready_when_db_connected(self):
        from app.main import app
        client = TestClient(app, raise_server_exceptions=False)

        with patch("app.api.v1.routers.health.check_db_connection", return_value=True):
            response = client.get("/health/ready")
        assert response.status_code == 200
        assert response.json()["status"] == "ready"

    def test_not_ready_when_db_unavailable(self):
        from app.main import app
        client = TestClient(app, raise_server_exceptions=False)

        with patch("app.api.v1.routers.health.check_db_connection", return_value=False):
            response = client.get("/health/ready")
        assert response.status_code == 503
        assert response.json()["status"] == "not_ready"

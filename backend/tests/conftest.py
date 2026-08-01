import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.api.routes import get_repository
from backend.infrastructure.fake_repositories import FakeSolicitudeRepository

@pytest.fixture(scope="function")
def fake_repository():
    """Create a fresh fake repository for each test."""
    return FakeSolicitudeRepository()

@pytest.fixture(scope="function")
def client(fake_repository):
    """Override the get_repository dependency to use the fake repository."""
    def override_get_repository():
        return fake_repository

    app.dependency_overrides[get_repository] = override_get_repository
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

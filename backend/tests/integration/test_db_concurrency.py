import asyncio
import os
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.infrastructure.database.connection import Base, get_db
from backend.app.main import app

# Skip if Postgres is not configured (we need it for real concurrency tests)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL or "postgres" not in DATABASE_URL:
    pytest.skip("Skipping concurrency test because no Postgres DATABASE_URL provided", allow_module_level=True)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    engine = create_engine(DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Recreate tables for clean state
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    except Exception:
        pytest.skip("Could not connect to database for integration tests", allow_module_level=True)
        return

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

@pytest.mark.asyncio
async def test_concurrent_status_updates():
    """
    Simulate multiple concurrent requests trying to process the same ServiceRequest.
    Verifies that the database correctly handles the TOCTOU race condition.
    """
    import httpx
    req_id = str(uuid.uuid4())

    # Use sync TestClient for setup
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/requests",
            json={
                "external_id": req_id,
                "type": "technical_support",
                "requester_name": "Test",
                "email": "test@test.com",
                "description": "Concurrency test",
                "priority": "high",
            },
        )
        assert res.status_code == 201

    # Fire 10 concurrent patch requests using AsyncClient
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        tasks = [
            client.patch(
                f"/api/v1/requests/{req_id}/status",
                json={"status": "in_progress", "justification": "concurrency test"}
            )
            for _ in range(10)
        ]

        results = await asyncio.gather(*tasks)

        status_codes = [r.status_code for r in results]

        # We should not get any internal server errors (500)
        assert 500 not in status_codes

        # At least one request should succeed
        assert 200 in status_codes

        # Verify final state is correct
        res = await client.get(f"/api/v1/requests/{req_id}")
        assert res.status_code == 200
        assert res.json()["status"] == "in_progress"

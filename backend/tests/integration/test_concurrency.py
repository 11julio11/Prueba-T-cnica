import pytest
from unittest.mock import MagicMock
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.domain.entities import InstitutionalRequest
from backend.app.domain.exceptions import DuplicateExternalIdError
from backend.app.infrastructure.database.request_repository_impl import PostgresRequestRepository
from backend.app.domain.value_objects import Priority, RequestType

@pytest.fixture
def valid_data() -> dict:
    return {
        "external_id": "EXT-CONC-001",
        "type": RequestType.TECHNICAL_SUPPORT,
        "requester_name": "Test User",
        "email": "test.user@example.com",
        "description": "Sample description for automated testing",
        "priority": Priority.HIGH,
    }

def test_repository_handles_concurrent_inserts(valid_data):
    """
    Test that simulates a race condition (TOCTOU).
    Two requests arrive at the same time. Both check `get_by_external_id` and see None.
    Both try to insert. The database throws an IntegrityError on the second commit.
    The repository must catch this IntegrityError and raise DuplicateExternalIdError.
    """
    session_mock = MagicMock(spec=Session)

    # 1. Simulate that the record does NOT exist yet (read phase)
    session_mock.get.return_value = None

    # 2. Simulate the database rejecting the commit due to unique constraint (write phase)
    session_mock.commit.side_effect = IntegrityError(
        "duplicate key value violates unique constraint", params={}, orig=Exception()
    )

    repo = PostgresRequestRepository(session_mock)
    request = InstitutionalRequest(**valid_data)

    # 3. Assert that the repository catches it and raises the domain exception
    with pytest.raises(DuplicateExternalIdError) as exc_info:
        repo.save(request)

    assert exc_info.value.external_id == "EXT-CONC-001"
    session_mock.rollback.assert_called_once()


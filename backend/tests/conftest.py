from unittest.mock import MagicMock

import pytest
from app.domain.entities import InstitutionalRequest
from app.domain.ports.request_repository import RequestRepository
from app.domain.use_cases import (
    RegisterInstitutionalRequest,
    UpdateInstitutionalRequestStatus,
)
from app.domain.value_objects import Priority, RequestType


@pytest.fixture
def repo_mock() -> MagicMock:
    return MagicMock(spec=RequestRepository)


@pytest.fixture
def register_use_case(repo_mock: MagicMock) -> RegisterInstitutionalRequest:
    return RegisterInstitutionalRequest(repo=repo_mock)


@pytest.fixture
def update_use_case(repo_mock: MagicMock) -> UpdateInstitutionalRequestStatus:
    return UpdateInstitutionalRequestStatus(repo=repo_mock)


@pytest.fixture
def valid_data() -> dict:
    return {
        "external_id": "EXT-001",
        "type": RequestType.TECHNICAL_SUPPORT,
        "requester_name": "Test User",
        "email": "test.user@example.com",
        "description": "Sample description for automated testing",
        "priority": Priority.HIGH,
    }


@pytest.fixture
def existing_request(valid_data: dict) -> InstitutionalRequest:
    return InstitutionalRequest(**valid_data)

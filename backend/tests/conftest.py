import os

# Inject a dummy DATABASE_URL so that Pydantic Settings doesn't fail during test collection
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")

import pytest

from backend.app.application.use_cases import (
    GetInstitutionalRequest,
    ListInstitutionalRequests,
    RegisterInstitutionalRequest,
    UpdateInstitutionalRequestStatus,
)
from backend.app.domain.entities import InstitutionalRequest
from backend.app.domain.ports.request_repository import RequestRepository
from backend.app.domain.value_objects import Priority, RequestType, Status


class FakeRequestRepository(RequestRepository):
    def __init__(self):
        self._db: dict[str, InstitutionalRequest] = {}

    def save(self, request: InstitutionalRequest) -> InstitutionalRequest:
        existing = self._db.get(str(request.external_id))
        if existing and id(existing) != id(request):
            from backend.app.domain.exceptions import DuplicateExternalIdError
            raise DuplicateExternalIdError(request.external_id)
        self._db[str(request.external_id)] = request
        return request

    def get_by_external_id(self, external_id: str) -> InstitutionalRequest | None:
        return self._db.get(str(external_id))

    def list_requests(
        self,
        status: Status | None = None,
        type: RequestType | None = None,
        priority: Priority | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[InstitutionalRequest]:
        results = list(self._db.values())
        if status:
            results = [r for r in results if r.status == status]
        if type:
            results = [r for r in results if r.type == type]
        if priority:
            results = [r for r in results if r.priority == priority]
        return results[offset : offset + limit]


@pytest.fixture
def fake_repo() -> FakeRequestRepository:
    return FakeRequestRepository()


@pytest.fixture
def register_use_case(fake_repo: FakeRequestRepository) -> RegisterInstitutionalRequest:
    return RegisterInstitutionalRequest(repo=fake_repo)


@pytest.fixture
def update_use_case(fake_repo: FakeRequestRepository) -> UpdateInstitutionalRequestStatus:
    return UpdateInstitutionalRequestStatus(repo=fake_repo)


@pytest.fixture
def get_use_case(fake_repo: FakeRequestRepository) -> GetInstitutionalRequest:
    return GetInstitutionalRequest(repo=fake_repo)


@pytest.fixture
def list_use_case(fake_repo: FakeRequestRepository) -> ListInstitutionalRequests:
    return ListInstitutionalRequests(repo=fake_repo)


@pytest.fixture
def valid_data() -> dict:
    return {
        "external_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "type": RequestType.TECHNICAL_SUPPORT,
        "requester_name": "Test User",
        "email": "test.user@example.com",
        "description": "Sample description for automated testing",
        "priority": Priority.HIGH,
    }


@pytest.fixture
def existing_request(valid_data: dict) -> InstitutionalRequest:
    return InstitutionalRequest(**(valid_data | {"status": Status.RECEIVED}))

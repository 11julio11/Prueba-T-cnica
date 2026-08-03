
from backend.app.domain.entities import InstitutionalRequest
from backend.app.domain.exceptions import DuplicateExternalIdError, RequestNotFoundError
from backend.app.domain.ports.request_repository import RequestRepository
from backend.app.domain.value_objects import Priority, RequestType, Status
from pydantic import EmailStr, UUID4


class RegisterInstitutionalRequest:
    def __init__(self, repo: RequestRepository) -> None:
        self._repo = repo

    def execute(
        self,
        external_id: UUID4,
        type: RequestType,
        requester_name: str,
        email: EmailStr,
        description: str,
        priority: Priority,
    ) -> InstitutionalRequest:
        existing = self._repo.get_by_external_id(external_id)
        if existing:
            raise DuplicateExternalIdError(external_id)

        new_request = InstitutionalRequest(
            external_id=external_id,
            type=type,
            requester_name=requester_name,
            email=email,
            status=Status.RECEIVED,
            description=description,
            priority=priority,
        )
        self._repo.save(new_request)
        return new_request


class UpdateInstitutionalRequestStatus:
    def __init__(self, repo: RequestRepository) -> None:
        self._repo = repo

    def execute(self, external_id: str, new_status: Status) -> InstitutionalRequest:
        request = self._repo.get_by_external_id(external_id)
        if not request:
            raise RequestNotFoundError(external_id)

        request.update_status(new_status)
        self._repo.save(request)
        return request


class GetInstitutionalRequest:
    def __init__(self, repo: RequestRepository) -> None:
        self._repo = repo

    def execute(self, external_id: str) -> InstitutionalRequest:
        request = self._repo.get_by_external_id(external_id)
        if not request:
            raise RequestNotFoundError(external_id)
        return request


class ListInstitutionalRequests:
    def __init__(self, repo: RequestRepository) -> None:
        self._repo = repo

    def execute(
        self,
        status: Status | None = None,
        type: RequestType | None = None,
        priority: Priority | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[InstitutionalRequest]:
        return self._repo.list_requests(
            status=status,
            type=type,
            priority=priority,
            limit=limit,
            offset=offset,
        )

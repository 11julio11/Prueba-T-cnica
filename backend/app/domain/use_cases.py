
from backend.app.domain.entities import InstitutionalRequest
from backend.app.domain.exceptions import DuplicateExternalIdError, RequestNotFoundError
from backend.app.domain.ports.request_repository import RequestRepository
from backend.app.domain.value_objects import Priority, RequestType, Status


class RegisterInstitutionalRequest:
    def __init__(self, repo: RequestRepository) -> None:
        self._repo = repo

    def execute(
        self,
        external_id: str,
        type: RequestType,
        requester_name: str,
        email: str,
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
            description=description,
            priority=priority,
        )
        self._repo.save(new_request)
        return new_request

class UpdateInstitutionalRequestStatus:
    def __init__(self, repo: RequestRepository) -> None:
        self._repo = repo

    def execute(self, external_id: str, new_status: Status) -> InstitutionalRequest:
        request_obj = self._repo.get_by_external_id(external_id)
        if not request_obj:
            raise RequestNotFoundError(external_id)

        request_obj.update_status(new_status)
        self._repo.save(request_obj)
        return request_obj

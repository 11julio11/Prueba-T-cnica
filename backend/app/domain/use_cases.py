
from app.domain.entities import InstitutionalRequest
from app.domain.exceptions import DuplicateExternalIdError, RequestNotFoundError
from app.domain.ports.request_repository import RequestRepository
from app.domain.value_objects import Priority, RequestType, Status


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
        existente = self._repo.get_by_external_id(external_id)
        if existente:
            raise DuplicateExternalIdError(external_id)

        nueva_solicitud = InstitutionalRequest(
            external_id=external_id,
            type=type,
            requester_name=requester_name,
            email=email,
            description=description,
            priority=priority,
        )
        self._repo.save(nueva_solicitud)
        return nueva_solicitud

class UpdateInstitutionalRequestStatus:
    def __init__(self, repo: RequestRepository) -> None:
        self._repo = repo

    def execute(self, external_id: str, new_status: Status) -> InstitutionalRequest:
        solicitud = self._repo.get_by_external_id(external_id)
        if not solicitud:
            raise RequestNotFoundError(external_id)

        solicitud.update_status(new_status)
        self._repo.save(solicitud)
        return solicitud

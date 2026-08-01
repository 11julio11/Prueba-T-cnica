from typing import Optional
from uuid import UUID

from app.domain.entities.service_request import ServiceRequest
from app.domain.exceptions import DuplicateExternalIdError, RequestNotFoundError
from app.domain.ports.request_repository import RequestRepository
from app.domain.value_objects.status import Status
from app.domain.value_objects.priority import Priority
from app.domain.value_objects.request_type import RequestType


class RequestService:

    def __init__(self, repo: RequestRepository) -> None:
        self._repo = repo

    def create(
        self,
        external_id: str,
        type: RequestType,
        requester_name: str,
        email: str,
        description: str,
        priority: Priority,
    ) -> ServiceRequest:
        existente = self._repo.obtener_por_identificador_externo(external_id)
        if existente:
            raise DuplicateExternalIdError(external_id)

        request = ServiceRequest(
            external_id=external_id,
            type=type,
            requester_name=requester_name,
            email=email,
            description=description,
            priority=priority,
        )
        return self._repo.guardar(request)

    def obtener(self, id: UUID) -> ServiceRequest:
        request = self._repo.get_by_id(id)
        if not request:
            raise RequestNotFoundError(id)
        return request

    def list_requests(
        self,
        status: Optional[Status] = None,
        type: Optional[RequestType] = None,
        priority: Optional[Priority] = None,
        limite: int = 100,
        offset: int = 0,
    ) -> list[ServiceRequest]:
        return self._repo.list_requests(
            status=status,
            type=type,
            priority=priority,
            limite=limite,
            offset=offset,
        )

    def update_status(self, id: UUID, nuevo_status: Status) -> ServiceRequest:
        request = self._repo.get_by_id(id)
        if not request:
            raise RequestNotFoundError(id)

        request.update_status(nuevo_status)
        return self._repo.actualizar(request)

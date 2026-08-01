from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.entities.service_request import ServiceRequest
from app.domain.value_objects.status import Status
from app.domain.value_objects.priority import Priority
from app.domain.value_objects.request_type import RequestType


class RequestRepository(ABC):

    @abstractmethod
    def guardar(self, request: ServiceRequest) -> ServiceRequest:
        """Persiste una nueva request y la retorna."""
        ...

    @abstractmethod
    def get_by_id(self, id: UUID) -> Optional[ServiceRequest]:
        """Retorna la request o None si no existe."""
        ...

    @abstractmethod
    def obtener_por_identificador_externo(
        self, external_id: str
    ) -> Optional[ServiceRequest]:
        """Retorna la request por su ID externo o None."""
        ...

    @abstractmethod
    def list_requests(
        self,
        status: Optional[Status] = None,
        type: Optional[RequestType] = None,
        priority: Optional[Priority] = None,
        limite: int = 100,
        offset: int = 0,
    ) -> list[ServiceRequest]:
        """Lista requests con filtros opcionales."""
        ...

    @abstractmethod
    def actualizar(self, request: ServiceRequest) -> ServiceRequest:
        """Actualiza una request existente."""
        ...

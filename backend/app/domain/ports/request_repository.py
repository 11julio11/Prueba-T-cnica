from abc import ABC, abstractmethod

from backend.app.domain.entities import InstitutionalRequest
from backend.app.domain.value_objects import Priority, RequestType, Status


class RequestRepository(ABC):
    @abstractmethod
    def save(self, request: InstitutionalRequest) -> InstitutionalRequest:
        """Persists a new or updated request and returns it."""
        ...

    @abstractmethod
    def get_by_external_id(self, external_id: str) -> InstitutionalRequest | None:
        """Returns the request by its external ID or None."""
        ...

    @abstractmethod
    def list_requests(
        self,
        status: Status | None = None,
        type: RequestType | None = None,
        priority: Priority | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[InstitutionalRequest]:
        """Lists requests with optional filters."""
        ...

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities import InstitutionalRequest
from app.domain.value_objects import Status, Priority, RequestType

class RequestRepository(ABC):
    @abstractmethod
    def save(self, request: InstitutionalRequest) -> InstitutionalRequest:
        """Persists a new or updated request and returns it."""
        ...

    @abstractmethod
    def get_by_external_id(self, external_id: str) -> Optional[InstitutionalRequest]:
        """Returns the request by its external ID or None."""
        ...

    @abstractmethod
    def list_requests(
        self,
        status: Optional[Status] = None,
        type: Optional[RequestType] = None,
        priority: Optional[Priority] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[InstitutionalRequest]:
        """Lists requests with optional filters."""
        ...

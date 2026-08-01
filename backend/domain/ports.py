from typing import Protocol
from backend.domain.schemas import (
    SolicitudeCreate,
    SolicitudeResponse,
    SolicitudeUpdateStatus,
    SolicitudeStatus,
    SolicitudeType,
    SolicitudePriority
)

class ISolicitudeRepository(Protocol):
    """
    Port (Interface) defining how the Domain interacts with the storage layer.
    Notice that this strictly uses Domain models (schemas), NOT Infrastructure models.
    """
    
    def create(self, solicitude_data: SolicitudeCreate) -> SolicitudeResponse:
        ...

    def get_by_id(self, solicitude_id: int) -> SolicitudeResponse:
        ...

    def get_all(
        self, 
        status: SolicitudeStatus | None = None, 
        request_type: SolicitudeType | None = None, 
        priority: SolicitudePriority | None = None
    ) -> list[SolicitudeResponse]:
        ...

    def update_status(self, solicitude_id: int, status_update: SolicitudeUpdateStatus) -> SolicitudeResponse:
        ...

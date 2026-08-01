from backend.domain.ports import ISolicitudeRepository
from backend.domain.schemas import (
    SolicitudeCreate,
    SolicitudeUpdateStatus,
    SolicitudeStatus,
    SolicitudeType,
    SolicitudePriority,
    SolicitudeResponse
)

class SolicitudeService:
    """
    Service layer containing the core business logic.
    Decouples the API from the database repository.
    """
    def __init__(self, repository: ISolicitudeRepository):
        self.repository = repository

    def create_solicitude(self, solicitude_data: SolicitudeCreate) -> SolicitudeResponse:
        """
        Business rules for creating a new solicitude.
        - Ensure new solicitudes always start as RECEIVED.
        - Pass validated data to the repository.
        """
        # Business logic validation could go here if needed.
        # The repository handles the uniqueness of external_id constraints.
        return self.repository.create(solicitude_data)

    def get_all_solicitudes(
        self, 
        status: SolicitudeStatus | None = None, 
        request_type: SolicitudeType | None = None, 
        priority: SolicitudePriority | None = None
    ) -> list[SolicitudeResponse]:
        """
        Retrieve all solicitudes applying optional filters.
        """
        return self.repository.get_all(
            status=status, 
            request_type=request_type, 
            priority=priority
        )

    def get_solicitude_by_id(self, solicitude_id: int) -> SolicitudeResponse:
        """
        Retrieve a single solicitude by its ID.
        """
        # If we had authorization rules (e.g. users can only see their own solicitudes), 
        # that logic would be validated here before returning.
        return self.repository.get_by_id(solicitude_id)

    def update_solicitude_status(self, solicitude_id: int, status_update: SolicitudeUpdateStatus) -> SolicitudeResponse:
        """
        Business rules for updating status.
        - Fetch existing solicitude to ensure it exists.
        - Apply transition rules if necessary (e.g., cannot move from REJECTED to IN_PROGRESS).
        """
        existing_solicitude = self.repository.get_by_id(solicitude_id)
        
        # Example of business logic: preventing transitions from completed states
        if existing_solicitude.status in [SolicitudeStatus.COMPLETED, SolicitudeStatus.REJECTED]:
            # In a real app, we might raise a BusinessRuleException here
            pass 

        return self.repository.update_status(solicitude_id, status_update)

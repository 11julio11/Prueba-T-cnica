from typing import Dict, List, Optional
from datetime import datetime

from backend.domain.ports import ISolicitudeRepository
from backend.domain.schemas import (
    SolicitudeCreate,
    SolicitudeUpdateStatus,
    SolicitudeStatus,
    SolicitudeType,
    SolicitudePriority,
    SolicitudeResponse
)
from backend.core.exceptions import ConflictException, NotFoundException

class FakeSolicitudeRepository(ISolicitudeRepository):
    def __init__(self):
        self._storage: Dict[int, SolicitudeResponse] = {}
        self._id_counter = 1

    def create(self, solicitude_data: SolicitudeCreate) -> SolicitudeResponse:
        # Verificamos restricción de unicidad para external_id
        for sol in self._storage.values():
            if sol.external_id == solicitude_data.external_id:
                raise ConflictException(f"Solicitude with external_id '{solicitude_data.external_id}' already exists.")

        new_solicitude = SolicitudeResponse(
            id=self._id_counter,
            external_id=solicitude_data.external_id,
            request_type=solicitude_data.request_type,
            requester_name=solicitude_data.requester_name,
            email=solicitude_data.email,
            description=solicitude_data.description,
            priority=solicitude_data.priority,
            status=SolicitudeStatus.RECEIVED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self._storage[self._id_counter] = new_solicitude
        self._id_counter += 1
        return new_solicitude

    def get_by_id(self, solicitude_id: int) -> SolicitudeResponse:
        if solicitude_id not in self._storage:
            raise NotFoundException(f"Solicitude with id '{solicitude_id}' not found.")
        return self._storage[solicitude_id]

    def get_all(
        self,
        status: Optional[SolicitudeStatus] = None,
        request_type: Optional[SolicitudeType] = None,
        priority: Optional[SolicitudePriority] = None
    ) -> List[SolicitudeResponse]:
        result = list(self._storage.values())
        if status:
            result = [s for s in result if s.status == status]
        if request_type:
            result = [s for s in result if s.request_type == request_type]
        if priority:
            result = [s for s in result if s.priority == priority]
        return result

    def update_status(self, solicitude_id: int, status_update: SolicitudeUpdateStatus) -> SolicitudeResponse:
        if solicitude_id not in self._storage:
            raise NotFoundException(f"Solicitude with id '{solicitude_id}' not found.")
        
        solicitude = self._storage[solicitude_id]
        updated_solicitude = solicitude.model_copy(
            update={
                "status": status_update.status,
                "updated_at": datetime.utcnow()
            }
        )
        self._storage[solicitude_id] = updated_solicitude
        return updated_solicitude

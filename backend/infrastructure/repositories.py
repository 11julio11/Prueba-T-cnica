from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.infrastructure.models import SolicitudeModel
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

class SolicitudeRepository(ISolicitudeRepository):
    def __init__(self, db: Session):
        self.db = db

    def _map_to_domain(self, model: SolicitudeModel) -> SolicitudeResponse:
        """Helper to map a SQLAlchemy model to a pure Domain Entity (Pydantic schema)."""
        return SolicitudeResponse.model_validate(model)

    def create(self, solicitude_data: SolicitudeCreate) -> SolicitudeResponse:
        """Creates a new solicitude in the database and returns a Domain Entity."""
        db_obj = SolicitudeModel(
            external_id=solicitude_data.external_id,
            request_type=solicitude_data.request_type,
            requester_name=solicitude_data.requester_name,
            email=solicitude_data.email,
            description=solicitude_data.description,
            priority=solicitude_data.priority,
            status=SolicitudeStatus.RECEIVED
        )
        try:
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return self._map_to_domain(db_obj)
        except IntegrityError:
            self.db.rollback()
            raise ConflictException(f"Solicitude with external_id '{solicitude_data.external_id}' already exists.")

    def get_by_id(self, solicitude_id: int) -> SolicitudeResponse:
        """Retrieves a solicitude by its internal ID and returns a Domain Entity."""
        obj = self.db.query(SolicitudeModel).filter(SolicitudeModel.id == solicitude_id).first()
        if not obj:
            raise NotFoundException(f"Solicitude with id '{solicitude_id}' not found.")
        return self._map_to_domain(obj)

    def get_all(self, 
                status: SolicitudeStatus | None = None, 
                request_type: SolicitudeType | None = None, 
                priority: SolicitudePriority | None = None) -> list[SolicitudeResponse]:
        """Retrieves all solicitudes with optional filtering as Domain Entities."""
        query = self.db.query(SolicitudeModel)
        
        if status:
            query = query.filter(SolicitudeModel.status == status)
        if request_type:
            query = query.filter(SolicitudeModel.request_type == request_type)
        if priority:
            query = query.filter(SolicitudeModel.priority == priority)
            
        return [self._map_to_domain(obj) for obj in query.all()]

    def update_status(self, solicitude_id: int, status_update: SolicitudeUpdateStatus) -> SolicitudeResponse:
        """Updates the status of an existing solicitude and returns the updated Domain Entity."""
        obj = self.db.query(SolicitudeModel).filter(SolicitudeModel.id == solicitude_id).first()
        if not obj:
            raise NotFoundException(f"Solicitude with id '{solicitude_id}' not found.")
            
        obj.status = status_update.status
        self.db.commit()
        self.db.refresh(obj)
        return self._map_to_domain(obj)

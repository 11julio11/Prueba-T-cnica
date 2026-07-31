from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.infrastructure.models import SolicitudeModel
from backend.domain.schemas import SolicitudeCreate, SolicitudeUpdateStatus, SolicitudeStatus, SolicitudeType, SolicitudePriority
from backend.core.exceptions import ConflictException, NotFoundException

class SolicitudeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, solicitude_data: SolicitudeCreate) -> SolicitudeModel:
        """Creates a new solicitude in the database."""
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
            return db_obj
        except IntegrityError:
            self.db.rollback()
            raise ConflictException(f"Solicitude with external_id '{solicitude_data.external_id}' already exists.")

    def get_by_id(self, solicitude_id: int) -> SolicitudeModel:
        """Retrieves a solicitude by its internal ID."""
        obj = self.db.query(SolicitudeModel).filter(SolicitudeModel.id == solicitude_id).first()
        if not obj:
            raise NotFoundException(f"Solicitude with id '{solicitude_id}' not found.")
        return obj

    def get_all(self, 
                status: SolicitudeStatus | None = None, 
                request_type: SolicitudeType | None = None, 
                priority: SolicitudePriority | None = None) -> list[SolicitudeModel]:
        """Retrieves all solicitudes with optional filtering."""
        query = self.db.query(SolicitudeModel)
        
        if status:
            query = query.filter(SolicitudeModel.status == status)
        if request_type:
            query = query.filter(SolicitudeModel.request_type == request_type)
        if priority:
            query = query.filter(SolicitudeModel.priority == priority)
            
        return query.all()

    def update_status(self, solicitude_id: int, status_update: SolicitudeUpdateStatus) -> SolicitudeModel:
        """Updates the status of an existing solicitude."""
        obj = self.get_by_id(solicitude_id)
        obj.status = status_update.status
        self.db.commit()
        self.db.refresh(obj)
        return obj

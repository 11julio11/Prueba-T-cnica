from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities.service_request import ServiceRequest
from app.domain.ports.request_repository import RequestRepository
from app.domain.value_objects.status import Status
from app.domain.value_objects.priority import Priority
from app.domain.value_objects.request_type import RequestType
from app.infrastructure.database.mapper import to_entity, to_model
from app.infrastructure.database.models import RequestModel


class PostgresRequestRepository(RequestRepository):

    def __init__(self, db: Session) -> None:
        self._db = db

    def guardar(self, request: ServiceRequest) -> ServiceRequest:
        model = to_model(request)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return to_entity(model)

    def get_by_id(self, id: UUID) -> Optional[ServiceRequest]:
        model = self._db.get(RequestModel, id)
        return to_entity(model) if model else None

    def obtener_por_identificador_externo(
        self, external_id: str
    ) -> Optional[ServiceRequest]:
        model = (
            self._db.query(RequestModel)
            .filter(RequestModel.external_id == external_id)
            .first()
        )
        return to_entity(model) if model else None

    def list_requests(
        self,
        status: Optional[Status] = None,
        type: Optional[RequestType] = None,
        priority: Optional[Priority] = None,
        limite: int = 100,
        offset: int = 0,
    ) -> list[ServiceRequest]:
        query = self._db.query(RequestModel)

        if status is not None:
            query = query.filter(RequestModel.status == status)
        if type is not None:
            query = query.filter(RequestModel.type == type)
        if priority is not None:
            query = query.filter(RequestModel.priority == priority)

        models = (
            query.order_by(RequestModel.created_at.desc())
            .offset(offset)
            .limit(limite)
            .all()
        )
        return [to_entity(m) for m in models]

    def actualizar(self, request: ServiceRequest) -> ServiceRequest:
        model = self._db.get(RequestModel, request.id)
        if model is None:
            raise ValueError(f"ServiceRequest {request.id} no existe en BD")

        model.status = request.status
        model.updated_at = request.updated_at
        self._db.commit()
        self._db.refresh(model)
        return to_entity(model)

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import uuid
from typing import Optional

from backend.app.domain.entities import InstitutionalRequest
from backend.app.domain.exceptions import DuplicateExternalIdError
from backend.app.domain.ports.request_repository import RequestRepository
from backend.app.domain.value_objects import Priority, RequestType, Status
from backend.app.infrastructure.database.mapper import to_entity, to_model
from backend.app.infrastructure.database.models import RequestModel


class PostgresRequestRepository(RequestRepository):
    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, request: InstitutionalRequest) -> InstitutionalRequest:
        try:
            model = to_model(request)
            model = self._db.merge(model)
            self._db.commit()
            return to_entity(model)
        except IntegrityError:
            self._db.rollback()
            raise DuplicateExternalIdError(request.external_id)

    def update_status(self, external_id: str, new_status: str) -> Optional[InstitutionalRequest]:
        if isinstance(external_id, str):
            parsed_id = uuid.UUID(external_id)
        else:
            parsed_id = external_id
        model = self._db.get(RequestModel, parsed_id)
        return to_entity(model) if model else None

    def get_by_external_id(self, external_id: str) -> Optional[InstitutionalRequest]:
        if isinstance(external_id, str):
            parsed_id = uuid.UUID(external_id)
        else:
            parsed_id = external_id
        model = self._db.get(RequestModel, parsed_id)
        return to_entity(model) if model else None

    def list_requests(
        self,
        status: Status | None = None,
        type: RequestType | None = None,
        priority: Priority | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[InstitutionalRequest]:
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
            .limit(limit)
            .all()
        )
        return [to_entity(m) for m in models]

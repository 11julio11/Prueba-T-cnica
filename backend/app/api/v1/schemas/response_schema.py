from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.value_objects.status import Status
from app.domain.value_objects.priority import Priority
from app.domain.value_objects.request_type import RequestType


class SolicitudResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    external_id: str
    type: RequestType
    requester_name: str
    email: str
    description: str
    priority: Priority
    status: Status
    created_at: datetime
    updated_at: datetime


class ListaSolicitudesResponse(BaseModel):
    total: int
    items: list[SolicitudResponse]

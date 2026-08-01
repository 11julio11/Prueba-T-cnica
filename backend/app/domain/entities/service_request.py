from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.domain.value_objects.status import Status
from app.domain.value_objects.priority import Priority
from app.domain.value_objects.request_type import RequestType


@dataclass
class ServiceRequest:
    external_id: str
    type: RequestType
    requester_name: str
    email: str
    description: str
    priority: Priority
    status: Status = field(default=Status.RECEIVED)
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def update_status(self, nuevo_status: Status) -> None:
        self.status = nuevo_status
        self.updated_at = datetime.now(timezone.utc)

    def __post_init__(self) -> None:
        if not self.external_id or not self.external_id.strip():
            raise ValueError("El identificador externo no puede estar vacío")
        if not self.requester_name or not self.requester_name.strip():
            raise ValueError("El nombre del solicitante no puede estar vacío")
        if not self.description or not self.description.strip():
            raise ValueError("La descripción no puede estar vacía")

from dataclasses import dataclass, field
from datetime import datetime, timezone

from backend.app.domain.value_objects import Priority, RequestType, Status


@dataclass
class InstitutionalRequest:
    external_id: str
    type: RequestType
    requester_name: str
    email: str
    description: str
    priority: Priority
    status: Status = field(default=Status.RECEIVED)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def update_status(self, new_status: Status) -> None:
        from backend.app.domain.exceptions import InvalidStatusTransitionError
        if self.status == Status.COMPLETED and new_status == Status.RECEIVED:
            raise InvalidStatusTransitionError(self.status, new_status)
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)

    def __post_init__(self) -> None:
        if not self.external_id or not self.external_id.strip():
            raise ValueError("The external identifier cannot be empty")
        if not self.requester_name or not self.requester_name.strip():
            raise ValueError("The requester name cannot be empty")
        if not self.description or not self.description.strip():
            raise ValueError("The description cannot be empty")

from datetime import datetime, timezone
import pydantic
from backend.app.domain.value_objects import Priority, RequestType, Status


class InstitutionalRequest(pydantic.BaseModel):
    external_id: pydantic.UUID4
    type: RequestType
    requester_name: str
    email: pydantic.EmailStr
    description: str
    priority: Priority
    status: Status
    created_at: datetime = pydantic.Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = pydantic.Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def update_status(self, new_status: Status) -> None:
        from backend.app.domain.exceptions import InvalidStatusTransitionError
        if self.status is Status.COMPLETED and new_status is Status.RECEIVED:
            raise InvalidStatusTransitionError(current=self.status, target=new_status)
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)

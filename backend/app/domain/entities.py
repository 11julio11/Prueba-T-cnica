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
    status: Status = Status.RECEIVED
    created_at: datetime = pydantic.Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = pydantic.Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def update_status(self, new_status: Status) -> None:
        from backend.app.domain.exceptions import InvalidStatusTransitionError
        if self.status in (Status.COMPLETED, Status.REJECTED):
            if new_status is not self.status:
                raise InvalidStatusTransitionError(current=self.status, target=new_status)
        if self.status == Status.IN_PROGRESS and new_status == Status.RECEIVED:
            raise InvalidStatusTransitionError(current=self.status, target=new_status)
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)

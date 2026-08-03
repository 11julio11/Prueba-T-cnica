from datetime import datetime

from pydantic import UUID4, BaseModel, ConfigDict, EmailStr

from backend.app.domain.value_objects import Priority, RequestType, Status


class ResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    external_id: UUID4
    type: RequestType
    requester_name: str
    email: EmailStr
    description: str
    priority: Priority
    status: Status
    created_at: datetime
    updated_at: datetime

class ListResponseSchema(BaseModel):
    total: int
    items: list[ResponseSchema]

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from backend.app.domain.value_objects import Priority, RequestType, Status


class ResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    external_id: str
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

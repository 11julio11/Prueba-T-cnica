from pydantic import BaseModel, EmailStr, Field, UUID4

from backend.app.domain.value_objects import Priority, RequestType, Status


class CreateRequestSchema(BaseModel):
    external_id: UUID4
    type: RequestType
    requester_name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    description: str = Field(..., min_length=10, max_length=2000)
    priority: Priority


class UpdateStatusSchema(BaseModel):
    status: Status

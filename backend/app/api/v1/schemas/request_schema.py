from pydantic import BaseModel, EmailStr, Field, field_validator

from backend.app.domain.value_objects import Priority, RequestType, Status


class CreateRequestSchema(BaseModel):
    external_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["EXT-2024-001"],
    )
    type: RequestType
    requester_name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    description: str = Field(..., min_length=10, max_length=2000)
    priority: Priority

    @field_validator("external_id", "requester_name", "description")
    @classmethod
    def not_only_spaces(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("The field cannot contain only spaces")
        return v.strip()

class UpdateStatusSchema(BaseModel):
    status: Status

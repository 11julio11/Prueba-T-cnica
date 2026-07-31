from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class SolicitudeType(str, Enum):
    PLATFORM_ACCESS = "acceso a plataforma"
    TECH_SUPPORT = "soporte técnico"
    ACADEMIC = "académica"
    ADMINISTRATIVE = "administrativa"

class SolicitudeStatus(str, Enum):
    RECEIVED = "recibida"
    IN_PROGRESS = "en proceso"
    COMPLETED = "completada"
    REJECTED = "rechazada"

class SolicitudePriority(str, Enum):
    LOW = "baja"
    MEDIUM = "media"
    HIGH = "alta"

class SolicitudeCreate(BaseModel):
    """Schema for creating a new solicitude."""
    external_id: str = Field(..., description="Unique identifier from the origin system")
    request_type: SolicitudeType
    requester_name: str = Field(..., min_length=2)
    email: EmailStr
    description: str = Field(..., min_length=10)
    priority: SolicitudePriority

class SolicitudeUpdateStatus(BaseModel):
    """Schema for updating the status of an existing solicitude."""
    status: SolicitudeStatus

class SolicitudeResponse(BaseModel):
    """Schema for returning solicitude details."""
    id: int
    external_id: str
    request_type: SolicitudeType
    requester_name: str
    email: EmailStr
    description: str
    priority: SolicitudePriority
    status: SolicitudeStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

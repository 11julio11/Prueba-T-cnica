from sqlalchemy import Column, String, Integer, DateTime, Enum, func
from backend.infrastructure.database import Base
from backend.domain.schemas import SolicitudeType, SolicitudeStatus, SolicitudePriority
import uuid

class SolicitudeModel(Base):
    __tablename__ = "solicitudes"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True, nullable=False)
    request_type = Column(Enum(SolicitudeType), nullable=False)
    requester_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    description = Column(String, nullable=False)
    priority = Column(Enum(SolicitudePriority), nullable=False)
    status = Column(Enum(SolicitudeStatus), nullable=False, default=SolicitudeStatus.RECEIVED)
    
    # Audit timestamps automatically managed by the DB
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

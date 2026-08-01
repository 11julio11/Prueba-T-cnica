from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.infrastructure.database import get_db
from backend.infrastructure.repositories import SolicitudeRepository
from backend.domain.ports import ISolicitudeRepository
from backend.domain.services import SolicitudeService
from backend.domain.schemas import (
    SolicitudeCreate, 
    SolicitudeResponse, 
    SolicitudeUpdateStatus,
    SolicitudeStatus,
    SolicitudeType,
    SolicitudePriority
)

router = APIRouter(prefix="/solicitudes", tags=["Solicitudes"])

def get_repository(db: Session = Depends(get_db)) -> ISolicitudeRepository:
    """Dependency injection for the infrastructure repository."""
    return SolicitudeRepository(db)

def get_solicitude_service(repository: ISolicitudeRepository = Depends(get_repository)) -> SolicitudeService:
    """Dependency injection for the domain service."""
    # We inject it into the domain service that expects a port (Interface)
    return SolicitudeService(repository)

@router.post("", response_model=SolicitudeResponse, status_code=status.HTTP_201_CREATED)
def create_solicitude(
    solicitude: SolicitudeCreate, 
    service: SolicitudeService = Depends(get_solicitude_service)
):
    """
    Register a new solicitude.
    """
    return service.create_solicitude(solicitude)

@router.get("", response_model=list[SolicitudeResponse])
def get_solicitudes(
    status: SolicitudeStatus | None = Query(None, description="Filter by status"),
    request_type: SolicitudeType | None = Query(None, description="Filter by request type"),
    priority: SolicitudePriority | None = Query(None, description="Filter by priority"),
    service: SolicitudeService = Depends(get_solicitude_service)
):
    """
    Retrieve solicitudes with optional filtering.
    """
    return service.get_all_solicitudes(status=status, request_type=request_type, priority=priority)

@router.get("/{id}", response_model=SolicitudeResponse)
def get_solicitude(
    id: int, 
    service: SolicitudeService = Depends(get_solicitude_service)
):
    """
    Retrieve a specific solicitude by ID.
    """
    return service.get_solicitude_by_id(id)

@router.patch("/{id}/estado", response_model=SolicitudeResponse)
def update_solicitude_status(
    id: int, 
    status_update: SolicitudeUpdateStatus, 
    service: SolicitudeService = Depends(get_solicitude_service)
):
    """
    Update the status of an existing solicitude.
    """
    return service.update_solicitude_status(id, status_update)

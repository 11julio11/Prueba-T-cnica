from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.infrastructure.database import get_db
from backend.infrastructure.repositories import SolicitudeRepository
from backend.domain.schemas import (
    SolicitudeCreate, 
    SolicitudeResponse, 
    SolicitudeUpdateStatus,
    SolicitudeStatus,
    SolicitudeType,
    SolicitudePriority
)

router = APIRouter(prefix="/solicitudes", tags=["Solicitudes"])

def get_repository(db: Session = Depends(get_db)) -> SolicitudeRepository:
    """Dependency injection for the repository."""
    return SolicitudeRepository(db)

@router.post("", response_model=SolicitudeResponse, status_code=status.HTTP_201_CREATED)
def create_solicitude(
    solicitude: SolicitudeCreate, 
    repo: SolicitudeRepository = Depends(get_repository)
):
    """
    Register a new solicitude.
    """
    # The repository handles the logic and uniqueness validation
    # in a real world scenario, business rules could be placed in a Service layer.
    return repo.create(solicitude)

@router.get("", response_model=list[SolicitudeResponse])
def get_solicitudes(
    status: SolicitudeStatus | None = Query(None, description="Filter by status"),
    request_type: SolicitudeType | None = Query(None, description="Filter by request type"),
    priority: SolicitudePriority | None = Query(None, description="Filter by priority"),
    repo: SolicitudeRepository = Depends(get_repository)
):
    """
    Retrieve solicitudes with optional filtering.
    """
    return repo.get_all(status=status, request_type=request_type, priority=priority)

@router.get("/{id}", response_model=SolicitudeResponse)
def get_solicitude(
    id: int, 
    repo: SolicitudeRepository = Depends(get_repository)
):
    """
    Retrieve a specific solicitude by ID.
    """
    return repo.get_by_id(id)

@router.patch("/{id}/estado", response_model=SolicitudeResponse)
def update_solicitude_status(
    id: int, 
    status_update: SolicitudeUpdateStatus, 
    repo: SolicitudeRepository = Depends(get_repository)
):
    """
    Update the status of an existing solicitude.
    """
    return repo.update_status(id, status_update)

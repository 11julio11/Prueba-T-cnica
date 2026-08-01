from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.database.connection import get_db
from app.infrastructure.database.solicitud_repository_impl import SolicitudRepositoryImpl
from app.domain.services.solicitud_service import SolicitudService


def get_solicitud_service(db: Session = Depends(get_db)) -> SolicitudService:
    repo = SolicitudRepositoryImpl(db)
    return SolicitudService(repo)

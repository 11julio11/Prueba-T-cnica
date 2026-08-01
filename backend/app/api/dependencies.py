from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.database.connection import get_db
from app.infrastructure.database.request_repository_impl import PostgresRequestRepository
from app.domain.services.request_service import RequestService


def get_solicitud_service(db: Session = Depends(get_db)) -> RequestService:
    repo = PostgresRequestRepository(db)
    return RequestService(repo)

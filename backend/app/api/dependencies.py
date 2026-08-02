from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.domain.ports.request_repository import RequestRepository
from backend.app.infrastructure.database.connection import get_db
from backend.app.infrastructure.database.request_repository_impl import (
    PostgresRequestRepository,
)


def get_request_repository(db: Session = Depends(get_db)) -> RequestRepository:
    return PostgresRequestRepository(db)

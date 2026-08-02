from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.infrastructure.database.connection import check_db_connection

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Check API availability")
def health() -> dict:
    return {"status": "ok", "service": "requests-api"}


@router.get("/health/ready", summary="Check PostgreSQL connection")
def health_ready() -> JSONResponse:
    db_ok = check_db_connection()
    if db_ok:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ready", "database": "connected"},
        )
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "not_ready", "database": "unavailable"},
    )

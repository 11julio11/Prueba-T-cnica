from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.domain.exceptions import DuplicateExternalIdError, RequestNotFoundError
from app.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(RequestNotFoundError)
    async def handle_not_found(
        request: Request, exc: RequestNotFoundError
    ) -> JSONResponse:
        logger.warning(
            "InstitutionalRequest not found",
            extra={"error": str(exc), "endpoint": str(request.url.path)},
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(DuplicateExternalIdError)
    async def handle_duplicate(
        request: Request, exc: DuplicateExternalIdError
    ) -> JSONResponse:
        logger.warning(
            "Duplicate identifier",
            extra={
                "external_id": exc.external_id,
                "endpoint": str(request.url.path),
            },
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning(
            "Validation error",
            extra={"error": str(exc), "endpoint": str(request.url.path)},
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def handle_generic(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "Unexpected internal error",
            extra={"error": type(exc).__name__, "endpoint": str(request.url.path)},
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Error interno del servidor"},
        )

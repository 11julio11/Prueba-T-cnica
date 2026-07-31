from fastapi import Request
from fastapi.responses import JSONResponse
from .logger import logger

class DomainException(Exception):
    """Base class for all domain-related exceptions."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

class NotFoundException(DomainException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, status_code=404)

class ConflictException(DomainException):
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message=message, status_code=409)

async def domain_exception_handler(request: Request, exc: DomainException):
    """
    Catches all custom DomainExceptions and returns a clean, structured JSON response.
    Avoids leaking sensitive technical details.
    """
    logger.warning("Domain exception occurred", exc=exc.message, status_code=exc.status_code, path=request.url.path)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

async def global_exception_handler(request: Request, exc: Exception):
    """
    Catches all unhandled exceptions to prevent leaking server details to the client.
    """
    logger.error("Unhandled server exception", exc=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."}
    )

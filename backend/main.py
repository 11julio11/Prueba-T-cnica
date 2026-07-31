from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.core.logger import setup_logger
from backend.core.exceptions import DomainException, domain_exception_handler, global_exception_handler
from backend.api.routes import router as solicitudes_router
from backend.infrastructure.database import get_db

# Initialize structured logging
setup_logger()

# Create FastAPI application instance
app = FastAPI(
    title="Solicitudes API",
    description="Backend service for managing institutional requests.",
    version="1.0.0"
)

# Register exception handlers
app.add_exception_handler(DomainException, domain_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Include routers
app.include_router(solicitudes_router)

@app.get("/health", tags=["Health"])
def health_check():
    """Verify API availability."""
    return {"status": "ok", "service": "solicitudes-api"}

@app.get("/health/ready", tags=["Health"])
def health_ready(db: Session = Depends(get_db)):
    """Verify connection with PostgreSQL."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return {"status": "not ready", "database": "disconnected", "detail": str(e)}

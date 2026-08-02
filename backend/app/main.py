from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.exception_handlers import register_exception_handlers
from app.api.v1.routers import health, requests
from app.config import settings
from app.infrastructure.logging.logger import get_logger, setup_logging

setup_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Iniciando aplicación", extra={"service": settings.app_name})
    yield
    logger.info("Cerrando aplicación")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API REST para gestión de requests institucionales",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(health.router)
app.include_router(requests.router, prefix="/api/v1")

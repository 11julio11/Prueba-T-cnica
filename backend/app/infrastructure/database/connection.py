from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.app.config import settings

engine_kwargs = {"pool_pre_ping": True}
if not settings.database_url.startswith("sqlite"):
    engine_kwargs["pool_size"] = settings.db_pool_size
    engine_kwargs["max_overflow"] = settings.db_max_overflow

engine = create_engine(settings.database_url, **engine_kwargs)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Checks if the database is reachable. Used by /health/ready."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

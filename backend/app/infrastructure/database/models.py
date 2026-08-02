from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.value_objects import Priority, RequestType, Status
from app.infrastructure.database.connection import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

class RequestModel(Base):
    __tablename__ = "requests"

    external_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
        index=True,
    )
    type: Mapped[RequestType] = mapped_column(
        Enum(RequestType, name="request_type_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    requester_name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[Priority] = mapped_column(
        Enum(Priority, name="priority_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    status: Mapped[Status] = mapped_column(
        Enum(Status, name="status_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=Status.RECEIVED,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
        onupdate=_utcnow,
    )

    # Composite index for frequent filter combinations
    __table_args__ = (
        Index("ix_requests_status_type_priority", "status", "type", "priority"),
    )

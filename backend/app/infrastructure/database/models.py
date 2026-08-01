import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.value_objects.estado import Estado
from app.domain.value_objects.prioridad import Prioridad
from app.domain.value_objects.tipo_solicitud import TipoSolicitud
from app.infrastructure.database.connection import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SolicitudModel(Base):
    __tablename__ = "solicitudes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    identificador_externo: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    tipo: Mapped[TipoSolicitud] = mapped_column(
        Enum(TipoSolicitud, name="tipo_solicitud_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    nombre_solicitante: Mapped[str] = mapped_column(String(200), nullable=False)
    correo: Mapped[str] = mapped_column(String(254), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    prioridad: Mapped[Prioridad] = mapped_column(
        Enum(Prioridad, name="prioridad_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    estado: Mapped[Estado] = mapped_column(
        Enum(Estado, name="estado_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=Estado.RECIBIDA,
        index=True,
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
        onupdate=_utcnow,
    )

    # Índice compuesto para filtros frecuentes
    __table_args__ = (
        Index("ix_solicitudes_estado_tipo_prioridad", "estado", "tipo", "prioridad"),
    )

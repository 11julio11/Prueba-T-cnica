"""Crear tabla solicitudes

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Crear tipos ENUM primero
    tipo_enum = sa.Enum(
        "acceso_plataforma", "soporte_tecnico", "academica", "administrativa",
        name="tipo_solicitud_enum",
    )
    estado_enum = sa.Enum(
        "recibida", "en_proceso", "completada", "rechazada",
        name="estado_enum",
    )
    prioridad_enum = sa.Enum(
        "baja", "media", "alta",
        name="prioridad_enum",
    )

    op.create_table(
        "solicitudes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("identificador_externo", sa.String(100), nullable=False, unique=True),
        sa.Column("tipo", tipo_enum, nullable=False),
        sa.Column("nombre_solicitante", sa.String(200), nullable=False),
        sa.Column("correo", sa.String(254), nullable=False),
        sa.Column("descripcion", sa.Text, nullable=False),
        sa.Column("prioridad", prioridad_enum, nullable=False),
        sa.Column("estado", estado_enum, nullable=False, server_default="recibida"),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "actualizado_en",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Índices individuales
    op.create_index("ix_solicitudes_identificador_externo", "solicitudes", ["identificador_externo"])
    op.create_index("ix_solicitudes_estado", "solicitudes", ["estado"])
    op.create_index("ix_solicitudes_tipo", "solicitudes", ["tipo"])
    op.create_index("ix_solicitudes_prioridad", "solicitudes", ["prioridad"])

    # Índice compuesto para filtros frecuentes
    op.create_index(
        "ix_solicitudes_estado_tipo_prioridad",
        "solicitudes",
        ["estado", "tipo", "prioridad"],
    )


def downgrade() -> None:
    op.drop_index("ix_solicitudes_estado_tipo_prioridad")
    op.drop_index("ix_solicitudes_prioridad")
    op.drop_index("ix_solicitudes_tipo")
    op.drop_index("ix_solicitudes_estado")
    op.drop_index("ix_solicitudes_identificador_externo")
    op.drop_table("solicitudes")

    op.execute("DROP TYPE IF EXISTS tipo_solicitud_enum")
    op.execute("DROP TYPE IF EXISTS estado_enum")
    op.execute("DROP TYPE IF EXISTS prioridad_enum")

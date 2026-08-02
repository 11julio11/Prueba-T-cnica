"""Crear tabla requests

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
import sqlalchemy as sa
from alembic import op

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Crear tipos ENUM primero
    tipo_enum = sa.Enum(
        "platform_access", "technical_support", "academic", "administrative",
        name="request_type_enum",
    )
    status_enum = sa.Enum(
        "received", "in_progress", "completed", "rejected",
        name="status_enum",
    )
    priority_enum = sa.Enum(
        "low", "medium", "high",
        name="priority_enum",
    )

    op.create_table(
        "requests",
        sa.Column("external_id", sa.String(100), primary_key=True, index=True),
        sa.Column("type", tipo_enum, nullable=False),
        sa.Column("requester_name", sa.String(200), nullable=False),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("priority", priority_enum, nullable=False),
        sa.Column("status", status_enum, nullable=False, server_default="received"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Índices individuales
    op.create_index("ix_solicitudes_status", "requests", ["status"])
    op.create_index("ix_solicitudes_tipo", "requests", ["type"])
    op.create_index("ix_solicitudes_priority", "requests", ["priority"])

    # Índice compuesto para filtros frecuentes
    op.create_index(
        "ix_requests_status_type_priority",
        "requests",
        ["status", "type", "priority"],
    )


def downgrade() -> None:
    op.drop_index("ix_requests_status_type_priority")
    op.drop_index("ix_solicitudes_priority")
    op.drop_index("ix_solicitudes_tipo")
    op.drop_index("ix_solicitudes_status")
    op.drop_table("requests")

    op.execute("DROP TYPE IF EXISTS request_type_enum")
    op.execute("DROP TYPE IF EXISTS status_enum")
    op.execute("DROP TYPE IF EXISTS priority_enum")

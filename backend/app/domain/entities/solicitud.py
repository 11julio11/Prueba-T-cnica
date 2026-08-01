from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.domain.value_objects.estado import Estado
from app.domain.value_objects.prioridad import Prioridad
from app.domain.value_objects.tipo_solicitud import TipoSolicitud


@dataclass
class Solicitud:
    identificador_externo: str
    tipo: TipoSolicitud
    nombre_solicitante: str
    correo: str
    descripcion: str
    prioridad: Prioridad
    estado: Estado = field(default=Estado.RECIBIDA)
    id: UUID = field(default_factory=uuid4)
    creado_en: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    actualizado_en: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def actualizar_estado(self, nuevo_estado: Estado) -> None:
        self.estado = nuevo_estado
        self.actualizado_en = datetime.now(timezone.utc)

    def __post_init__(self) -> None:
        if not self.identificador_externo or not self.identificador_externo.strip():
            raise ValueError("El identificador externo no puede estar vacío")
        if not self.nombre_solicitante or not self.nombre_solicitante.strip():
            raise ValueError("El nombre del solicitante no puede estar vacío")
        if not self.descripcion or not self.descripcion.strip():
            raise ValueError("La descripción no puede estar vacía")

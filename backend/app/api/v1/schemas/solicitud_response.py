from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.value_objects.estado import Estado
from app.domain.value_objects.prioridad import Prioridad
from app.domain.value_objects.tipo_solicitud import TipoSolicitud


class SolicitudResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    identificador_externo: str
    tipo: TipoSolicitud
    nombre_solicitante: str
    correo: str
    descripcion: str
    prioridad: Prioridad
    estado: Estado
    creado_en: datetime
    actualizado_en: datetime


class ListaSolicitudesResponse(BaseModel):
    total: int
    items: list[SolicitudResponse]

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.domain.value_objects.estado import Estado
from app.domain.value_objects.prioridad import Prioridad
from app.domain.value_objects.tipo_solicitud import TipoSolicitud


class CrearSolicitudRequest(BaseModel):
    identificador_externo: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["EXT-2024-001"],
    )
    tipo: TipoSolicitud
    nombre_solicitante: str = Field(..., min_length=2, max_length=200)
    correo: EmailStr
    descripcion: str = Field(..., min_length=10, max_length=2000)
    prioridad: Prioridad

    @field_validator("identificador_externo", "nombre_solicitante", "descripcion")
    @classmethod
    def no_solo_espacios(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El campo no puede contener solo espacios")
        return v.strip()


class ActualizarEstadoRequest(BaseModel):
    estado: Estado

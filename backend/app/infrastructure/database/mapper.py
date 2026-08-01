from app.domain.entities.solicitud import Solicitud
from app.infrastructure.database.models import SolicitudModel


def to_entity(model: SolicitudModel) -> Solicitud:
    return Solicitud(
        id=model.id,
        identificador_externo=model.identificador_externo,
        tipo=model.tipo,
        nombre_solicitante=model.nombre_solicitante,
        correo=model.correo,
        descripcion=model.descripcion,
        prioridad=model.prioridad,
        estado=model.estado,
        creado_en=model.creado_en,
        actualizado_en=model.actualizado_en,
    )


def to_model(entity: Solicitud) -> SolicitudModel:
    return SolicitudModel(
        id=entity.id,
        identificador_externo=entity.identificador_externo,
        tipo=entity.tipo,
        nombre_solicitante=entity.nombre_solicitante,
        correo=entity.correo,
        descripcion=entity.descripcion,
        prioridad=entity.prioridad,
        estado=entity.estado,
        creado_en=entity.creado_en,
        actualizado_en=entity.actualizado_en,
    )

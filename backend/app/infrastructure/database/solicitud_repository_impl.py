from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities.solicitud import Solicitud
from app.domain.ports.solicitud_repository import SolicitudRepository
from app.domain.value_objects.estado import Estado
from app.domain.value_objects.prioridad import Prioridad
from app.domain.value_objects.tipo_solicitud import TipoSolicitud
from app.infrastructure.database.mapper import to_entity, to_model
from app.infrastructure.database.models import SolicitudModel


class SolicitudRepositoryImpl(SolicitudRepository):

    def __init__(self, db: Session) -> None:
        self._db = db

    def guardar(self, solicitud: Solicitud) -> Solicitud:
        model = to_model(solicitud)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return to_entity(model)

    def obtener_por_id(self, id: UUID) -> Optional[Solicitud]:
        model = self._db.get(SolicitudModel, id)
        return to_entity(model) if model else None

    def obtener_por_identificador_externo(
        self, identificador_externo: str
    ) -> Optional[Solicitud]:
        model = (
            self._db.query(SolicitudModel)
            .filter(SolicitudModel.identificador_externo == identificador_externo)
            .first()
        )
        return to_entity(model) if model else None

    def listar(
        self,
        estado: Optional[Estado] = None,
        tipo: Optional[TipoSolicitud] = None,
        prioridad: Optional[Prioridad] = None,
        limite: int = 100,
        offset: int = 0,
    ) -> list[Solicitud]:
        query = self._db.query(SolicitudModel)

        if estado is not None:
            query = query.filter(SolicitudModel.estado == estado)
        if tipo is not None:
            query = query.filter(SolicitudModel.tipo == tipo)
        if prioridad is not None:
            query = query.filter(SolicitudModel.prioridad == prioridad)

        models = (
            query.order_by(SolicitudModel.creado_en.desc())
            .offset(offset)
            .limit(limite)
            .all()
        )
        return [to_entity(m) for m in models]

    def actualizar(self, solicitud: Solicitud) -> Solicitud:
        model = self._db.get(SolicitudModel, solicitud.id)
        if model is None:
            raise ValueError(f"Solicitud {solicitud.id} no existe en BD")

        model.estado = solicitud.estado
        model.actualizado_en = solicitud.actualizado_en
        self._db.commit()
        self._db.refresh(model)
        return to_entity(model)

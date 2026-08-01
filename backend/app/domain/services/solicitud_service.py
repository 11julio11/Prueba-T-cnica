from typing import Optional
from uuid import UUID

from app.domain.entities.solicitud import Solicitud
from app.domain.exceptions import IdentificadorDuplicado, SolicitudNoEncontrada
from app.domain.ports.solicitud_repository import SolicitudRepository
from app.domain.value_objects.estado import Estado
from app.domain.value_objects.prioridad import Prioridad
from app.domain.value_objects.tipo_solicitud import TipoSolicitud


class SolicitudService:

    def __init__(self, repo: SolicitudRepository) -> None:
        self._repo = repo

    def crear(
        self,
        identificador_externo: str,
        tipo: TipoSolicitud,
        nombre_solicitante: str,
        correo: str,
        descripcion: str,
        prioridad: Prioridad,
    ) -> Solicitud:
        existente = self._repo.obtener_por_identificador_externo(identificador_externo)
        if existente:
            raise IdentificadorDuplicado(identificador_externo)

        solicitud = Solicitud(
            identificador_externo=identificador_externo,
            tipo=tipo,
            nombre_solicitante=nombre_solicitante,
            correo=correo,
            descripcion=descripcion,
            prioridad=prioridad,
        )
        return self._repo.guardar(solicitud)

    def obtener(self, id: UUID) -> Solicitud:
        solicitud = self._repo.obtener_por_id(id)
        if not solicitud:
            raise SolicitudNoEncontrada(id)
        return solicitud

    def listar(
        self,
        estado: Optional[Estado] = None,
        tipo: Optional[TipoSolicitud] = None,
        prioridad: Optional[Prioridad] = None,
        limite: int = 100,
        offset: int = 0,
    ) -> list[Solicitud]:
        return self._repo.listar(
            estado=estado,
            tipo=tipo,
            prioridad=prioridad,
            limite=limite,
            offset=offset,
        )

    def actualizar_estado(self, id: UUID, nuevo_estado: Estado) -> Solicitud:
        solicitud = self._repo.obtener_por_id(id)
        if not solicitud:
            raise SolicitudNoEncontrada(id)

        solicitud.actualizar_estado(nuevo_estado)
        return self._repo.actualizar(solicitud)

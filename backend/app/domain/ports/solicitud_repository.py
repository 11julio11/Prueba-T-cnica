from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.entities.solicitud import Solicitud
from app.domain.value_objects.estado import Estado
from app.domain.value_objects.prioridad import Prioridad
from app.domain.value_objects.tipo_solicitud import TipoSolicitud


class SolicitudRepository(ABC):

    @abstractmethod
    def guardar(self, solicitud: Solicitud) -> Solicitud:
        """Persiste una nueva solicitud y la retorna."""
        ...

    @abstractmethod
    def obtener_por_id(self, id: UUID) -> Optional[Solicitud]:
        """Retorna la solicitud o None si no existe."""
        ...

    @abstractmethod
    def obtener_por_identificador_externo(
        self, identificador_externo: str
    ) -> Optional[Solicitud]:
        """Retorna la solicitud por su ID externo o None."""
        ...

    @abstractmethod
    def listar(
        self,
        estado: Optional[Estado] = None,
        tipo: Optional[TipoSolicitud] = None,
        prioridad: Optional[Prioridad] = None,
        limite: int = 100,
        offset: int = 0,
    ) -> list[Solicitud]:
        """Lista solicitudes con filtros opcionales."""
        ...

    @abstractmethod
    def actualizar(self, solicitud: Solicitud) -> Solicitud:
        """Actualiza una solicitud existente."""
        ...

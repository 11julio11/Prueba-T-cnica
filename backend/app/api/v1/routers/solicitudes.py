import time
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_solicitud_service
from app.api.v1.schemas.solicitud_request import ActualizarEstadoRequest, CrearSolicitudRequest
from app.api.v1.schemas.solicitud_response import ListaSolicitudesResponse, SolicitudResponse
from app.domain.services.solicitud_service import SolicitudService
from app.domain.value_objects.estado import Estado
from app.domain.value_objects.prioridad import Prioridad
from app.domain.value_objects.tipo_solicitud import TipoSolicitud
from app.infrastructure.logging.logger import TimingContext, get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/solicitudes", tags=["Solicitudes"])


@router.post(
    "",
    response_model=SolicitudResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva solicitud",
)
def crear_solicitud(
    body: CrearSolicitudRequest,
    service: SolicitudService = Depends(get_solicitud_service),
) -> SolicitudResponse:
    with TimingContext() as t:
        solicitud = service.crear(
            identificador_externo=body.identificador_externo,
            tipo=body.tipo,
            nombre_solicitante=body.nombre_solicitante,
            correo=body.correo,
            descripcion=body.descripcion,
            prioridad=body.prioridad,
        )

    logger.info(
        "Solicitud creada",
        extra={
            "solicitud_id": str(solicitud.id),
            "identificador_externo": solicitud.identificador_externo,
            "method": "POST",
            "endpoint": "/solicitudes",
            "status_code": 201,
            "duration_ms": t.elapsed_ms,
        },
    )
    return SolicitudResponse.model_validate(solicitud.__dict__)


@router.get(
    "",
    response_model=ListaSolicitudesResponse,
    summary="Listar solicitudes con filtros opcionales",
)
def listar_solicitudes(
    estado: Optional[Estado] = Query(None),
    tipo: Optional[TipoSolicitud] = Query(None),
    prioridad: Optional[Prioridad] = Query(None),
    limite: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    service: SolicitudService = Depends(get_solicitud_service),
) -> ListaSolicitudesResponse:
    with TimingContext() as t:
        solicitudes = service.listar(
            estado=estado,
            tipo=tipo,
            prioridad=prioridad,
            limite=limite,
            offset=offset,
        )

    logger.info(
        "Solicitudes listadas",
        extra={
            "method": "GET",
            "endpoint": "/solicitudes",
            "status_code": 200,
            "duration_ms": t.elapsed_ms,
        },
    )
    items = [SolicitudResponse.model_validate(s.__dict__) for s in solicitudes]
    return ListaSolicitudesResponse(total=len(items), items=items)


@router.get(
    "/{id}",
    response_model=SolicitudResponse,
    summary="Consultar una solicitud específica",
)
def obtener_solicitud(
    id: UUID,
    service: SolicitudService = Depends(get_solicitud_service),
) -> SolicitudResponse:
    with TimingContext() as t:
        solicitud = service.obtener(id)

    logger.info(
        "Solicitud consultada",
        extra={
            "solicitud_id": str(id),
            "method": "GET",
            "endpoint": f"/solicitudes/{id}",
            "status_code": 200,
            "duration_ms": t.elapsed_ms,
        },
    )
    return SolicitudResponse.model_validate(solicitud.__dict__)


@router.patch(
    "/{id}/estado",
    response_model=SolicitudResponse,
    summary="Actualizar el estado de una solicitud",
)
def actualizar_estado(
    id: UUID,
    body: ActualizarEstadoRequest,
    service: SolicitudService = Depends(get_solicitud_service),
) -> SolicitudResponse:
    with TimingContext() as t:
        solicitud = service.actualizar_estado(id, body.estado)

    logger.info(
        "Estado actualizado",
        extra={
            "solicitud_id": str(id),
            "method": "PATCH",
            "endpoint": f"/solicitudes/{id}/estado",
            "status_code": 200,
            "duration_ms": t.elapsed_ms,
        },
    )
    return SolicitudResponse.model_validate(solicitud.__dict__)

import time
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_solicitud_service
from app.api.v1.schemas.request_schema import ActualizarEstadoRequest, CrearSolicitudRequest
from app.api.v1.schemas.response_schema import ListaSolicitudesResponse, SolicitudResponse
from app.domain.services.request_service import RequestService
from app.domain.value_objects.status import Status
from app.domain.value_objects.priority import Priority
from app.domain.value_objects.request_type import RequestType
from app.infrastructure.logging.logger import TimingContext, get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/requests", tags=["Solicitudes"])


@router.post(
    "",
    response_model=SolicitudResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva request",
)
def create_request(
    body: CrearSolicitudRequest,
    service: RequestService = Depends(get_solicitud_service),
) -> SolicitudResponse:
    with TimingContext() as t:
        request = service.create(
            external_id=body.external_id,
            type=body.type,
            requester_name=body.requester_name,
            email=body.email,
            description=body.description,
            priority=body.priority,
        )

    logger.info(
        "ServiceRequest creada",
        extra={
            "request_id": str(request.id),
            "external_id": request.external_id,
            "method": "POST",
            "endpoint": "/requests",
            "status_code": 201,
            "duration_ms": t.elapsed_ms,
        },
    )
    return SolicitudResponse.model_validate(request.__dict__)


@router.get(
    "",
    response_model=ListaSolicitudesResponse,
    summary="Listar requests con filtros opcionales",
)
def listar_solicitudes(
    status: Optional[Status] = Query(None),
    type: Optional[RequestType] = Query(None),
    priority: Optional[Priority] = Query(None),
    limite: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    service: RequestService = Depends(get_solicitud_service),
) -> ListaSolicitudesResponse:
    with TimingContext() as t:
        requests = service.list_requests(
            status=status,
            type=type,
            priority=priority,
            limite=limite,
            offset=offset,
        )

    logger.info(
        "Solicitudes listadas",
        extra={
            "method": "GET",
            "endpoint": "/requests",
            "status_code": 200,
            "duration_ms": t.elapsed_ms,
        },
    )
    items = [SolicitudResponse.model_validate(s.__dict__) for s in requests]
    return ListaSolicitudesResponse(total=len(items), items=items)


@router.get(
    "/{id}",
    response_model=SolicitudResponse,
    summary="Consultar una request específica",
)
def obtener_solicitud(
    id: UUID,
    service: RequestService = Depends(get_solicitud_service),
) -> SolicitudResponse:
    with TimingContext() as t:
        request = service.obtener(id)

    logger.info(
        "ServiceRequest consultada",
        extra={
            "request_id": str(id),
            "method": "GET",
            "endpoint": f"/requests/{id}",
            "status_code": 200,
            "duration_ms": t.elapsed_ms,
        },
    )
    return SolicitudResponse.model_validate(request.__dict__)


@router.patch(
    "/{id}/status",
    response_model=SolicitudResponse,
    summary="Actualizar el status de una request",
)
def update_status(
    id: UUID,
    body: ActualizarEstadoRequest,
    service: RequestService = Depends(get_solicitud_service),
) -> SolicitudResponse:
    with TimingContext() as t:
        request = service.update_status(id, body.status)

    logger.info(
        "Status actualizado",
        extra={
            "request_id": str(id),
            "method": "PATCH",
            "endpoint": f"/requests/{id}/status",
            "status_code": 200,
            "duration_ms": t.elapsed_ms,
        },
    )
    return SolicitudResponse.model_validate(request.__dict__)

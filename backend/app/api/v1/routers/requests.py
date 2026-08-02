from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_request_repository
from app.api.v1.schemas.request_schema import UpdateStatusSchema, CreateRequestSchema
from app.api.v1.schemas.response_schema import ListResponseSchema, ResponseSchema
from app.domain.ports.request_repository import RequestRepository
from app.domain.use_cases import RegisterInstitutionalRequest, UpdateInstitutionalRequestStatus
from app.domain.value_objects import Status, Priority, RequestType
from app.domain.exceptions import RequestNotFoundError, DuplicateExternalIdError
from app.infrastructure.logging.logger import TimingContext, get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/requests", tags=["Solicitudes"])


@router.post(
    "",
    response_model=ResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva request",
)
def create_request(
    body: CreateRequestSchema,
    repo: RequestRepository = Depends(get_request_repository),
) -> ResponseSchema:
    with TimingContext() as t:
        use_case = RegisterInstitutionalRequest(repo)
        request = use_case.execute(
            external_id=body.external_id,
            type=body.type,
            requester_name=body.requester_name,
            email=body.email,
            description=body.description,
            priority=body.priority,
        )

    logger.info(
        "InstitutionalRequest created",
        extra={
            "external_id": request.external_id,
            "method": "POST",
            "endpoint": "/requests",
            "status_code": 201,
            "duration_ms": t.elapsed_ms,
        },
    )
    return ResponseSchema.model_validate(request.__dict__)


@router.get(
    "",
    response_model=ListResponseSchema,
    summary="Listar requests con filtros opcionales",
)
def list_requests(
    status: Optional[Status] = Query(None),
    type: Optional[RequestType] = Query(None),
    priority: Optional[Priority] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    repo: RequestRepository = Depends(get_request_repository),
) -> ListResponseSchema:
    with TimingContext() as t:
        requests = repo.list_requests(
            status=status,
            type=type,
            priority=priority,
            limit=limit,
            offset=offset,
        )

    logger.info(
        "Requests listed",
        extra={
            "method": "GET",
            "endpoint": "/requests",
            "status_code": 200,
            "duration_ms": t.elapsed_ms,
        },
    )
    items = [ResponseSchema.model_validate(s.__dict__) for s in requests]
    return ListResponseSchema(total=len(items), items=items)


@router.get(
    "/{external_id}",
    response_model=ResponseSchema,
    summary="Consultar una request específica por external_id",
)
def get_request(
    external_id: str,
    repo: RequestRepository = Depends(get_request_repository),
) -> ResponseSchema:
    with TimingContext() as t:
        request = repo.get_by_external_id(external_id)
        if not request:
            raise RequestNotFoundError(external_id)

    logger.info(
        "InstitutionalRequest retrieved",
        extra={
            "external_id": external_id,
            "method": "GET",
            "endpoint": f"/requests/{external_id}",
            "status_code": 200,
            "duration_ms": t.elapsed_ms,
        },
    )
    return ResponseSchema.model_validate(request.__dict__)


@router.patch(
    "/{external_id}/status",
    response_model=ResponseSchema,
    summary="Actualizar el status de una request",
)
def update_status(
    external_id: str,
    body: UpdateStatusSchema,
    repo: RequestRepository = Depends(get_request_repository),
) -> ResponseSchema:
    with TimingContext() as t:
        use_case = UpdateInstitutionalRequestStatus(repo)
        request = use_case.execute(external_id, body.status)

    logger.info(
        "Status updated",
        extra={
            "external_id": external_id,
            "method": "PATCH",
            "endpoint": f"/requests/{external_id}/status",
            "status_code": 200,
            "duration_ms": t.elapsed_ms,
        },
    )
    return ResponseSchema.model_validate(request.__dict__)

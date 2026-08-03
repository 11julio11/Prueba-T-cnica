
from fastapi import APIRouter, Depends, Query, status

from backend.app.api.dependencies import get_request_repository
from backend.app.api.v1.schemas.request_schema import CreateRequestSchema, UpdateStatusSchema
from backend.app.api.v1.schemas.response_schema import ListResponseSchema, ResponseSchema
from backend.app.domain.exceptions import RequestNotFoundError
from backend.app.domain.ports.request_repository import RequestRepository
from backend.app.application.use_cases import (
    GetInstitutionalRequest,
    ListInstitutionalRequests,
    RegisterInstitutionalRequest,
    UpdateInstitutionalRequestStatus,
)
from backend.app.domain.value_objects import Priority, RequestType, Status
from backend.app.infrastructure.logging.logger import TimingContext, get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/requests", tags=["Requests"])


@router.post(
    "",
    response_model=ResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new institutional request",
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
    summary="List requests with optional filters",
)
def list_requests(
    status: Status | None = Query(None),
    type: RequestType | None = Query(None),
    priority: Priority | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    repo: RequestRepository = Depends(get_request_repository),
) -> ListResponseSchema:
    with TimingContext() as t:
        use_case = ListInstitutionalRequests(repo)
        requests = use_case.execute(
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
    summary="Retrieve a specific request by external_id",
)
def get_request(
    external_id: str,
    repo: RequestRepository = Depends(get_request_repository),
) -> ResponseSchema:
    with TimingContext() as t:
        use_case = GetInstitutionalRequest(repo)
        request = use_case.execute(external_id)

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
    summary="Update the status of a request",
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

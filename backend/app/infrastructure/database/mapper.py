from app.domain.entities.service_request import ServiceRequest
from app.infrastructure.database.models import RequestModel


def to_entity(model: RequestModel) -> ServiceRequest:
    return ServiceRequest(
        id=model.id,
        external_id=model.external_id,
        type=model.type,
        requester_name=model.requester_name,
        email=model.email,
        description=model.description,
        priority=model.priority,
        status=model.status,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def to_model(entity: ServiceRequest) -> RequestModel:
    return RequestModel(
        id=entity.id,
        external_id=entity.external_id,
        type=entity.type,
        requester_name=entity.requester_name,
        email=entity.email,
        description=entity.description,
        priority=entity.priority,
        status=entity.status,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )

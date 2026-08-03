
import pytest
from backend.app.domain.exceptions import (
    DuplicateExternalIdError,
    InvalidStatusTransitionError,
    RequestNotFoundError,
)
from backend.app.domain.value_objects import Status


def test_register_institutional_request_success(register_use_case, fake_repo, valid_data):
    result = register_use_case.execute(**valid_data)

    assert str(result.external_id) == valid_data["external_id"]
    assert result.status == Status.RECEIVED
    assert result.priority == valid_data["priority"]
    assert result.type == valid_data["type"]
    assert result.created_at is not None
    assert result.updated_at is not None
    
    # We verify that it was saved in the in-memory repository
    saved_req = fake_repo.get_by_external_id(valid_data["external_id"])
    assert saved_req is not None
    assert str(saved_req.external_id) == valid_data["external_id"]

def test_register_institutional_request_duplicate(register_use_case, fake_repo, valid_data, existing_request):
    # We manually save to the fake repo to simulate the duplicate.
    fake_repo.save(existing_request)

    with pytest.raises(DuplicateExternalIdError):
        register_use_case.execute(**valid_data)

def test_update_institutional_request_status_success(update_use_case, fake_repo, existing_request):
    # Setup initial state
    fake_repo.save(existing_request)

    assert existing_request.status is Status.RECEIVED

    result = update_use_case.execute(existing_request.external_id, Status.IN_PROGRESS)

    assert result.status is Status.IN_PROGRESS
    
    # Verify in-memory state changed
    saved_req = fake_repo.get_by_external_id(existing_request.external_id)
    assert saved_req.status is Status.IN_PROGRESS

def test_update_institutional_request_status_not_found(update_use_case, fake_repo):
    with pytest.raises(RequestNotFoundError):
        update_use_case.execute("a9b6c4b1-8b77-4b7b-832f-7c1c5a7e6b5d", Status.IN_PROGRESS)

def test_update_institutional_request_status_invalid_transition(update_use_case, fake_repo, existing_request):
    existing_request.status = Status.COMPLETED
    fake_repo.save(existing_request)

    with pytest.raises(InvalidStatusTransitionError):
        update_use_case.execute(existing_request.external_id, Status.RECEIVED)


def test_get_institutional_request_success(get_use_case, fake_repo, existing_request):
    fake_repo.save(existing_request)

    result = get_use_case.execute(existing_request.external_id)

    assert result is not None
    assert result.external_id == existing_request.external_id


def test_get_institutional_request_not_found(get_use_case, fake_repo):
    with pytest.raises(RequestNotFoundError):
        get_use_case.execute("a9b6c4b1-8b77-4b7b-832f-7c1c5a7e6b5d")


def test_list_institutional_requests(list_use_case, fake_repo, existing_request):
    fake_repo.save(existing_request)

    results = list_use_case.execute()
    
    assert len(results) == 1
    assert results[0].external_id == existing_request.external_id


def test_list_institutional_requests_with_filters(list_use_case, fake_repo, existing_request):
    fake_repo.save(existing_request)
    
    # Save another request with different properties
    from backend.app.domain.entities import InstitutionalRequest
    from backend.app.domain.value_objects import Priority, RequestType, Status
    
    other_request = InstitutionalRequest(
        external_id="3d813cbb-47fb-42ba-91df-831e1593ac29",
        type=RequestType.ADMINISTRATIVE,
        requester_name="Other User",
        email="other@example.com",
        status=Status.RECEIVED,
        description="Other desc",
        priority=Priority.LOW
    )
    fake_repo.save(other_request)

    # Filter by type that matches existing_request (TECHNICAL_SUPPORT)
    results = list_use_case.execute(type=RequestType.TECHNICAL_SUPPORT)
    assert len(results) == 1
    assert str(results[0].external_id) == str(existing_request.external_id)

    # Filter by priority that matches other_request (LOW)
    results2 = list_use_case.execute(priority=Priority.LOW)
    assert len(results2) == 1
    assert str(results2[0].external_id) == "3d813cbb-47fb-42ba-91df-831e1593ac29"

    # Filter by status (both are RECEIVED by default)
    results3 = list_use_case.execute(status=Status.RECEIVED)
    assert len(results3) == 2

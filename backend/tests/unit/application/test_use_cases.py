
import pytest
from backend.app.domain.exceptions import (
    DuplicateExternalIdError,
    InvalidStatusTransitionError,
    RequestNotFoundError,
)
from backend.app.domain.value_objects import Status


def test_register_institutional_request_success(register_use_case, repo_mock, valid_data):
    repo_mock.get_by_external_id.return_value = None
    repo_mock.save.side_effect = lambda req: req

    result = register_use_case.execute(**valid_data)

    assert result.external_id == valid_data["external_id"]
    assert result.status == Status.RECEIVED
    assert result.priority == valid_data["priority"]
    assert result.type == valid_data["type"]
    assert result.created_at is not None
    assert result.updated_at is not None
    repo_mock.get_by_external_id.assert_called_once_with(valid_data["external_id"])
    repo_mock.save.assert_called_once()

def test_register_institutional_request_duplicate(register_use_case, repo_mock, valid_data, existing_request):
    repo_mock.get_by_external_id.return_value = existing_request

    with pytest.raises(DuplicateExternalIdError):
        register_use_case.execute(**valid_data)

def test_update_institutional_request_status_success(update_use_case, repo_mock, existing_request):
    repo_mock.get_by_external_id.return_value = existing_request
    repo_mock.save.side_effect = lambda req: req

    assert existing_request.status == Status.RECEIVED

    result = update_use_case.execute(existing_request.external_id, Status.IN_PROGRESS)

    assert result.status == Status.IN_PROGRESS
    repo_mock.save.assert_called_once()

def test_update_institutional_request_status_not_found(update_use_case, repo_mock):
    repo_mock.get_by_external_id.return_value = None

    with pytest.raises(RequestNotFoundError):
        update_use_case.execute("EXT-999", Status.IN_PROGRESS)

def test_update_institutional_request_status_invalid_transition(update_use_case, repo_mock, existing_request):
    existing_request.status = Status.COMPLETED
    repo_mock.get_by_external_id.return_value = existing_request

    with pytest.raises(InvalidStatusTransitionError):
        update_use_case.execute(existing_request.external_id, Status.RECEIVED)

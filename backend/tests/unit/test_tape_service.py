from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import (
    NotAuthorisedError,
    TapeHasNoTracksError,
    TapeNotFoundError,
    TapeNotInDraftError,
)
from app.models.tape import TapeStatus
from app.services import tape_service


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.mark.asyncio
async def test_create_tape_success(mock_db):
    # Arrange: fake tape the repository will return
    mock_tape = MagicMock()
    mock_tape.id = 1
    mock_tape.title = "Summer Mix"
    mock_tape.cassette_style = "classic"
    mock_tape.length_minutes = 60
    mock_tape.sender_id = 42

    mock_repo_instance = MagicMock()
    mock_repo_instance.create = AsyncMock(return_value=mock_tape)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        result = await tape_service.create_tape(
            db=mock_db,
            title="Summer Mix",
            cassette_style="classic",
            length_minutes=60,
            sender_id=42,
        )

    assert result.title == "Summer Mix"
    assert result.sender_id == 42


@pytest.mark.asyncio
async def test_get_tape_success(mock_db):
    mock_tape = MagicMock()
    mock_tape.id = 1
    mock_tape.sender_id = 42

    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_id = AsyncMock(return_value=mock_tape)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        result = await tape_service.get_tape(db=mock_db, tape_id=1, user_id=42)

    assert result.id == 1
    assert result.sender_id == 42


@pytest.mark.asyncio
async def test_get_tape_not_found(mock_db):
    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_id = AsyncMock(return_value=None)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        with pytest.raises(TapeNotFoundError) as exc_info:
            await tape_service.get_tape(db=mock_db, tape_id=999, user_id=42)

    assert exc_info.value.message == "Tape not found"


@pytest.mark.asyncio
async def test_get_tape_wrong_user(mock_db):
    mock_tape = MagicMock()
    mock_tape.id = 1
    mock_tape.sender_id = 99  # different user

    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_id = AsyncMock(return_value=mock_tape)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        with pytest.raises(NotAuthorisedError) as exc_info:
            await tape_service.get_tape(db=mock_db, tape_id=1, user_id=42)

    assert exc_info.value.message == "Not authorised"


@pytest.mark.asyncio
async def test_mark_ready_not_found(mock_db):
    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_id = AsyncMock(return_value=None)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        with pytest.raises(TapeNotFoundError):
            await tape_service.mark_ready(db=mock_db, tape_id=999, user_id=42)


@pytest.mark.asyncio
async def test_mark_ready_wrong_user(mock_db):
    mock_tape = MagicMock()
    mock_tape.sender_id = 99  # different user

    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_id = AsyncMock(return_value=mock_tape)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        with pytest.raises(NotAuthorisedError):
            await tape_service.mark_ready(db=mock_db, tape_id=1, user_id=42)


@pytest.mark.asyncio
async def test_mark_ready_no_tracks(mock_db):
    mock_tape = MagicMock()
    mock_tape.sender_id = 42
    mock_tape.status = TapeStatus.draft
    mock_tape.tracks = []

    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_id = AsyncMock(return_value=mock_tape)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        with pytest.raises(TapeHasNoTracksError):
            await tape_service.mark_ready(db=mock_db, tape_id=1, user_id=42)


@pytest.mark.asyncio
async def test_mark_ready_not_draft(mock_db):
    mock_tape = MagicMock()
    mock_tape.sender_id = 42
    mock_tape.status = TapeStatus.ready
    mock_tape.tracks = [MagicMock()]

    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_id = AsyncMock(return_value=mock_tape)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        with pytest.raises(TapeNotInDraftError):
            await tape_service.mark_ready(db=mock_db, tape_id=1, user_id=42)


@pytest.mark.asyncio
async def test_mark_ready_success(mock_db):
    mock_tape = MagicMock()
    mock_tape.sender_id = 42
    mock_tape.status = TapeStatus.draft
    mock_tape.tracks = [MagicMock()]

    mock_updated_tape = MagicMock()
    mock_updated_tape.status = TapeStatus.ready

    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_id = AsyncMock(return_value=mock_tape)
    mock_repo_instance.update_status = AsyncMock(return_value=mock_updated_tape)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        result = await tape_service.mark_ready(db=mock_db, tape_id=1, user_id=42)

    assert result.status == TapeStatus.ready
    mock_repo_instance.update_status.assert_called_once_with(
        mock_tape, TapeStatus.ready
    )

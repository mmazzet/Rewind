from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.models.tape import TapeStatus
from app.models.track import TrackSide
from app.services import track_service


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.mark.asyncio
async def test_create_track_success(mock_db):
    # Arrange: fake track the repository will return
    mock_track = MagicMock()
    mock_track.id = 1
    mock_track.title = "Test Title Track"
    mock_track.artist = "The Zombies"
    mock_track.duration_seconds = 240

    mock_tape = MagicMock()
    mock_tape.sender_id = 1
    mock_tape.length_minutes = 60
    mock_tape.status = TapeStatus.draft

    mock_tape_repo = MagicMock()
    mock_tape_repo.get_by_id = AsyncMock(return_value=mock_tape)

    mock_track_repo = MagicMock()
    mock_track_repo.add_track = AsyncMock(return_value=mock_track)
    mock_track_repo.get_side_duration = AsyncMock(return_value=0)

    with (
        patch("app.services.track_service.TapeRepository", return_value=mock_tape_repo),
        patch(
            "app.services.track_service.TrackRepository", return_value=mock_track_repo
        ),
    ):

        result = await track_service.add_track(
            db=mock_db,
            tape_id=1,
            user_id=1,
            spotify_track_id="spotify123",
            title="Test Title Track",
            artist="The Zombies",
            duration_seconds=240,
            side=TrackSide.A,
            position=1,
        )

    assert result.title == "Test Title Track"
    assert result.artist == "The Zombies"
    assert result.duration_seconds == 240


async def test_add_track_tape_not_found(mock_db):
    mock_tape_repo = MagicMock()
    mock_tape_repo.get_by_id = AsyncMock(return_value=None)

    with patch(
        "app.services.track_service.TapeRepository", return_value=mock_tape_repo
    ):
        with pytest.raises(HTTPException) as exc_info:
            await track_service.add_track(
                db=mock_db,
                tape_id=999,  # Non-existent tape ID
                user_id=1,
                spotify_track_id="spotify123",
                title="Test Title Track",
                artist="The Zombies",
                duration_seconds=240,
                side=TrackSide.A,
                position=1,
            )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Tape not found"


async def test_add_track_wrong_user(mock_db):
    mock_tape = MagicMock()
    mock_tape.sender_id = 2  # Different user ID
    mock_tape.length_minutes = 60

    mock_tape_repo = MagicMock()
    mock_tape_repo.get_by_id = AsyncMock(return_value=mock_tape)

    with patch(
        "app.services.track_service.TapeRepository", return_value=mock_tape_repo
    ):
        with pytest.raises(HTTPException) as exc_info:
            await track_service.add_track(
                db=mock_db,
                tape_id=1,
                user_id=1,  # User ID does not match tape sender ID
                spotify_track_id="spotify123",
                title="Test Title Track",
                artist="The Zombies",
                duration_seconds=240,
                side=TrackSide.A,
                position=1,
            )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Not authorised"


async def test_add_track_side_limit_exceeded(mock_db):
    mock_tape = MagicMock()
    mock_tape.sender_id = 1
    mock_tape.length_minutes = 60

    mock_tape_repo = MagicMock()
    mock_tape_repo.get_by_id = AsyncMock(return_value=mock_tape)
    mock_tape.status = TapeStatus.draft

    mock_track_repo = MagicMock()
    # Simulate that the current side duration is already at the limit
    mock_track_repo.get_side_duration = AsyncMock(
        return_value=1700
    )  # 30 minutes in seconds

    with (
        patch("app.services.track_service.TapeRepository", return_value=mock_tape_repo),
        patch(
            "app.services.track_service.TrackRepository", return_value=mock_track_repo
        ),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await track_service.add_track(
                db=mock_db,
                tape_id=1,
                user_id=1,
                spotify_track_id="spotify123",
                title="Test Title Track",
                artist="The Zombies",
                duration_seconds=240,
                side=TrackSide.A,
                position=1,
            )

    assert exc_info.value.status_code == 422
    assert exc_info.value.detail == "Side time limit exceeded"


async def test_remove_track_success(mock_db):
    mock_tape = MagicMock()
    mock_tape.sender_id = 1
    mock_tape.status = TapeStatus.draft
    mock_tape_repo = MagicMock()
    mock_tape_repo.get_by_id = AsyncMock(return_value=mock_tape)

    mock_track_repo = MagicMock()
    mock_track_repo.delete_track = AsyncMock()

    with (
        patch(
            "app.services.track_service.TapeRepository",
            return_value=mock_tape_repo,
        ),
        patch(
            "app.services.track_service.TrackRepository",
            return_value=mock_track_repo,
        ),
    ):
        await track_service.remove_track(
            db=mock_db,
            tape_id=123,
            track_id=456,
            user_id=1,
        )

    mock_track_repo.delete_track.assert_awaited_once_with(456)


async def test_remove_track_tape_not_found(mock_db):
    mock_tape_repo = MagicMock()
    mock_tape_repo.get_by_id = AsyncMock(return_value=None)

    with patch(
        "app.services.track_service.TapeRepository", return_value=mock_tape_repo
    ):
        with pytest.raises(HTTPException) as exc_info:
            await track_service.remove_track(
                db=mock_db,
                tape_id=999,  # Non-existent tape ID
                track_id=1,
                user_id=1,
            )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Tape not found"


async def test_remove_track_wrong_user(mock_db):
    mock_tape = MagicMock()
    mock_tape.sender_id = 2  # Different user ID
    mock_tape.status = TapeStatus.draft

    mock_tape_repo = MagicMock()
    mock_tape_repo.get_by_id = AsyncMock(return_value=mock_tape)

    with patch(
        "app.services.track_service.TapeRepository", return_value=mock_tape_repo
    ):
        with pytest.raises(HTTPException) as exc_info:
            await track_service.remove_track(
                db=mock_db,
                tape_id=1,
                track_id=1,
                user_id=1,  # User ID does not match tape sender ID
            )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Not authorised"


async def test_add_track_at_exact_side_limit(mock_db):
    mock_tape = MagicMock()
    mock_tape.sender_id = 1
    mock_tape.length_minutes = 60
    mock_tape.status = TapeStatus.draft

    mock_tape_repo = MagicMock()
    mock_tape_repo.get_by_id = AsyncMock(return_value=mock_tape)

    mock_track = MagicMock()
    mock_track.id = 2
    mock_track.title = "Test Title Track"
    mock_track.artist = "The Zombies"
    mock_track.duration_seconds = 240

    mock_track_repo = MagicMock()
    # Side already has 1560 seconds. Adding 240 makes exactly 1800 (the limit).
    mock_track_repo.get_side_duration = AsyncMock(return_value=1560)
    mock_track_repo.add_track = AsyncMock(return_value=mock_track)

    with (
        patch("app.services.track_service.TapeRepository", return_value=mock_tape_repo),
        patch(
            "app.services.track_service.TrackRepository", return_value=mock_track_repo
        ),
    ):
        result = await track_service.add_track(
            db=mock_db,
            tape_id=1,
            user_id=1,
            spotify_track_id="spotify123",
            title="Test Title Track",
            artist="The Zombies",
            duration_seconds=240,
            side=TrackSide.A,
            position=1,
        )

    assert result.title == "Test Title Track"
    assert result.artist == "The Zombies"
    assert result.duration_seconds == 240


@pytest.mark.asyncio
async def test_create_track_fails_when_status_not_draft(mock_db):
    # Arrange: a tape that is not in draft status

    mock_tape = MagicMock()
    mock_tape.sender_id = 1
    mock_tape.length_minutes = 60
    mock_tape.status = TapeStatus.claimed  # Different from draft

    mock_tape_repo = MagicMock()
    mock_tape_repo.get_by_id = AsyncMock(return_value=mock_tape)

    with (
        patch("app.services.track_service.TapeRepository", return_value=mock_tape_repo),
    ):

        with pytest.raises(HTTPException) as exc_info:
            await track_service.add_track(
                db=mock_db,
                tape_id=1,
                user_id=1,
                spotify_track_id="spotify123",
                title="Test Title Track",
                artist="The Zombies",
                duration_seconds=240,
                side=TrackSide.A,
                position=1,
            )
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Tape is not in draft status"


async def test_remove_track_fails_when_tape_not_in_draft(mock_db):
    mock_tape = MagicMock()
    mock_tape.sender_id = 1
    mock_tape.status = TapeStatus.claimed  # Not in draft status
    mock_tape_repo = MagicMock()
    mock_tape_repo.get_by_id = AsyncMock(return_value=mock_tape)

    with (
        patch(
            "app.services.track_service.TapeRepository",
            return_value=mock_tape_repo,
        ),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await track_service.remove_track(
                db=mock_db,
                tape_id=123,
                track_id=456,
                user_id=1,
            )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Tape is not in draft status"

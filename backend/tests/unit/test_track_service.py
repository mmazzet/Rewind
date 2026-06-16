from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

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

    mock_track_repo = MagicMock()
    # Simulate that the current side duration is already at the limit
    mock_track_repo.get_side_duration = AsyncMock(
        return_value=3600
    )  # 60 minutes in seconds

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
            tape_id=1,
            track_id=1,
            user_id=1,
        )

    mock_track_repo.delete_track.assert_awaited_once_with(1)


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

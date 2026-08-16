from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import (
    NotAuthorisedError,
    SpotifyNotConnectedError,
    SpotifyUnavailableError,
    TapeNotFoundError,
)
from app.services.spotify_service import SpotifyService
from tests.fakes import FakeSpotifyClient

# --- Fixtures ---


@pytest.fixture
def fake_client():
    return FakeSpotifyClient()


@pytest.fixture
def service(fake_client):
    return SpotifyService(client=fake_client)


@pytest.fixture
def mock_token_repo():
    repo = MagicMock()
    token = MagicMock()
    token.access_token = "fake_access_token"
    repo.get_by_user_id = AsyncMock(return_value=token)
    repo.upsert = AsyncMock()
    return repo


@pytest.fixture
def mock_tape_repo():
    repo = MagicMock()
    tape = MagicMock()
    tape.id = 1
    tape.title = "Summer Mix"
    tape.sender_id = 42
    tape.tracks = [MagicMock(spotify_track_id="track_1")]
    repo.get_by_id = AsyncMock(return_value=tape)
    return repo


# --- search_tracks ---


@pytest.mark.asyncio
async def test_search_tracks_returns_formatted_results(service):
    results = await service.search_tracks("beatles")

    assert len(results) == 1
    track = results[0]
    assert track["spotify_track_id"] == "mock_1"
    assert track["title"] == "Mock result for beatles"
    assert track["artist"] == "Mock Artist"
    assert track["album"] == "Mock Album"
    assert track["duration_seconds"] == 200


@pytest.mark.asyncio
async def test_search_tracks_malformed_response_raises(service, fake_client):
    # Simulate Spotify returning something unexpected
    fake_client.search = AsyncMock(return_value={"unexpected": "data"})

    with pytest.raises(SpotifyUnavailableError):
        await service.search_tracks("beatles")


# --- handle_oauth_callback ---


@pytest.mark.asyncio
async def test_handle_oauth_callback_stores_tokens(service, mock_token_repo):
    await service.handle_oauth_callback(
        code="auth_code_123",
        user_id=42,
        token_repo=mock_token_repo,
    )

    mock_token_repo.upsert.assert_awaited_once()
    call_kwargs = mock_token_repo.upsert.call_args.kwargs
    assert call_kwargs["user_id"] == 42
    assert call_kwargs["access_token"] == "fake_access_token"
    assert call_kwargs["refresh_token"] == "fake_refresh_token"
    assert isinstance(call_kwargs["expires_at"], datetime)


# --- export_tape_to_spotify ---


@pytest.mark.asyncio
async def test_export_tape_returns_playlist_url(
    service, mock_token_repo, mock_tape_repo
):
    url = await service.export_tape_to_spotify(
        tape_id=1,
        user_id=42,
        token_repo=mock_token_repo,
        tape_repo=mock_tape_repo,
    )

    assert url == "https://open.spotify.com/playlist/fake123"


@pytest.mark.asyncio
async def test_export_tape_spotify_not_connected(
    service, mock_token_repo, mock_tape_repo
):
    # No token stored for this user
    mock_token_repo.get_by_user_id = AsyncMock(return_value=None)

    with pytest.raises(SpotifyNotConnectedError):
        await service.export_tape_to_spotify(
            tape_id=1,
            user_id=42,
            token_repo=mock_token_repo,
            tape_repo=mock_tape_repo,
        )


@pytest.mark.asyncio
async def test_export_tape_not_found(service, mock_token_repo, mock_tape_repo):
    mock_tape_repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(TapeNotFoundError):
        await service.export_tape_to_spotify(
            tape_id=999,
            user_id=42,
            token_repo=mock_token_repo,
            tape_repo=mock_tape_repo,
        )


@pytest.mark.asyncio
async def test_export_tape_wrong_user(service, mock_token_repo, mock_tape_repo):
    # Tape belongs to user 99, not 42
    mock_tape_repo.get_by_id.return_value.sender_id = 99

    with pytest.raises(NotAuthorisedError):
        await service.export_tape_to_spotify(
            tape_id=1,
            user_id=42,
            token_repo=mock_token_repo,
            tape_repo=mock_tape_repo,
        )

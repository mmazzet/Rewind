from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_user_id_from_cookie
from app.db.session import get_db
from app.repositories.spotify_token_repository import SpotifyTokenRepository
from app.repositories.tape_repository import TapeRepository
from app.schemas.spotify import SpotifyExportResponse, SpotifySearchResponse
from app.services.spotify_service import spotify_service

router = APIRouter(prefix="/spotify", tags=["spotify"])


@router.get("/search", response_model=SpotifySearchResponse)
async def search_tracks(
    q: str = Query(..., min_length=1, max_length=100),
    _user_id: int = Depends(get_user_id_from_cookie),
):
    tracks = await spotify_service.search_tracks(q)
    return SpotifySearchResponse(tracks=tracks)


@router.get("/auth")
async def spotify_auth(
    _user_id: int = Depends(get_user_id_from_cookie),
):
    """Redirect the user to Spotify's OAuth consent screen."""
    url = spotify_service.get_auth_url()
    return RedirectResponse(url=url)


@router.post("/callback")
async def spotify_callback_post(
    code: str,
    user_id: int = Depends(get_user_id_from_cookie),
    db: AsyncSession = Depends(get_db),
):
    """Accept the Spotify auth code from the frontend and exchange it for tokens."""
    token_repo = SpotifyTokenRepository(db)
    await spotify_service.handle_oauth_callback(
        code=code,
        user_id=user_id,
        token_repo=token_repo,
    )
    return {"status": "connected"}


@router.get("/callback")
async def spotify_callback(
    code: str | None = Query(default=None),
    error: str | None = Query(default=None),
    user_id: int = Depends(get_user_id_from_cookie),
    db: AsyncSession = Depends(get_db),
):
    """Handle Spotify's redirect after the user grants or denies permission."""
    frontend_url = settings.public_base_url

    if error or not code:
        return RedirectResponse(url=f"{frontend_url}/outbox?spotify=denied")

    token_repo = SpotifyTokenRepository(db)
    await spotify_service.handle_oauth_callback(
        code=code,
        user_id=user_id,
        token_repo=token_repo,
    )

    return RedirectResponse(url=f"{frontend_url}/outbox?spotify=connected")


@router.post("/export/{tape_id}", response_model=SpotifyExportResponse)
async def export_tape(
    tape_id: int,
    user_id: int = Depends(get_user_id_from_cookie),
    db: AsyncSession = Depends(get_db),
):
    """Create a Spotify playlist from a sent tape."""
    token_repo = SpotifyTokenRepository(db)
    tape_repo = TapeRepository(db)

    playlist_url = await spotify_service.export_tape_to_spotify(
        tape_id=tape_id,
        user_id=user_id,
        token_repo=token_repo,
        tape_repo=tape_repo,
    )

    return SpotifyExportResponse(spotify_playlist_url=playlist_url)

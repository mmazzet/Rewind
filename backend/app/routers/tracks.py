from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_user_id_from_cookie
from app.db.session import get_db
from app.schemas.track import AddTrackRequest, TrackResponse
from app.services import track_service

router = APIRouter(prefix="/tapes", tags=["tracks"])


@router.post("/{tape_id}/tracks", response_model=TrackResponse, status_code=201)
async def add_track(
    tape_id: int,
    body: AddTrackRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_user_id_from_cookie),
):
    track = await track_service.add_track(
        db=db,
        tape_id=tape_id,
        user_id=user_id,
        spotify_track_id=body.spotify_track_id,
        title=body.title,
        artist=body.artist,
        duration_seconds=body.duration_seconds,
        side=body.side,
        position=body.position,
    )
    return track


@router.delete("/{tape_id}/tracks/{track_id}", status_code=204)
async def remove_track(
    tape_id: int,
    track_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_user_id_from_cookie),
):
    await track_service.remove_track(
        db=db,
        tape_id=tape_id,
        track_id=track_id,
        user_id=user_id,
    )

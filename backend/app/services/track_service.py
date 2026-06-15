from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.track import Track, TrackSide
from app.repositories.tape_repository import TapeRepository
from app.repositories.track_repository import TrackRepository


async def add_track(
    db: AsyncSession,
    tape_id: int,
    user_id: int,
    spotify_track_id: str,
    title: str,
    artist: str,
    duration_seconds: int,
    side: TrackSide,
    position: int,
) -> Track:
    tape_repository = TapeRepository(db)
    track_repository = TrackRepository(db)

    tape = await tape_repository.get_by_id(tape_id)

    if tape is None:
        raise HTTPException(status_code=404, detail="Tape not found")

    if tape.sender_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorised")

    side_limit_seconds = (tape.length_minutes // 2) * 60
    current_duration = await track_repository.get_side_duration(tape_id, side)

    if current_duration + duration_seconds > side_limit_seconds:
        raise HTTPException(status_code=422, detail="Side time limit exceeded")

    return await track_repository.add_track(
        tape_id=tape_id,
        spotify_track_id=spotify_track_id,
        title=title,
        artist=artist,
        duration_seconds=duration_seconds,
        side=side,
        position=position,
    )


async def remove_track(
    db: AsyncSession,
    tape_id: int,
    track_id: int,
    user_id: int,
) -> None:
    tape_repository = TapeRepository(db)
    track_repository = TrackRepository(db)

    tape = await tape_repository.get_by_id(tape_id)

    if tape is None:
        raise HTTPException(status_code=404, detail="Tape not found")

    if tape.sender_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorised")

    await track_repository.delete_track(track_id)

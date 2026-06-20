from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.track import Track, TrackSide


class TrackRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_track(
        self,
        tape_id: int,
        spotify_track_id: str,
        title: str,
        artist: str,
        duration_seconds: int,
        side: TrackSide,
        position: int,
    ) -> Track:
        new_track = Track(
            tape_id=tape_id,
            spotify_track_id=spotify_track_id,
            title=title,
            artist=artist,
            duration_seconds=duration_seconds,
            side=side,
            position=position,
        )
        self.db.add(new_track)
        await self.db.commit()
        await self.db.refresh(new_track)
        return new_track

    async def delete_track(self, track_id: int) -> None:
        result = await self.db.execute(select(Track).where(Track.id == track_id))
        track = result.scalars().first()
        if track:
            await self.db.delete(track)
            await self.db.commit()

    async def get_side_duration(self, tape_id: int, side: TrackSide) -> int:
        result = await self.db.execute(
            select(func.coalesce(func.sum(Track.duration_seconds), 0))
            .where(Track.tape_id == tape_id)
            .where(Track.side == side)
        )
        return result.scalar()

    async def get_track_by_id(self, track_id: int) -> Track | None:
        result = await self.db.execute(select(Track).where(Track.id == track_id))
        return result.scalars().first()

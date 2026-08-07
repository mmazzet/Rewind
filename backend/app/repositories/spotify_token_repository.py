from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.spotify_token import SpotifyToken


class SpotifyTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: int) -> SpotifyToken | None:
        result = await self.db.execute(
            select(SpotifyToken).where(SpotifyToken.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def upsert(
        self,
        user_id: int,
        access_token: str,
        refresh_token: str | None,
        expires_at: datetime,
    ) -> SpotifyToken:
        token = await self.get_by_user_id(user_id)

        if token:
            token.access_token = access_token
            token.refresh_token = refresh_token
            token.expires_at = expires_at
        else:
            token = SpotifyToken(
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
            )
            self.db.add(token)

        await self.db.commit()
        await self.db.refresh(token)
        return token

    async def delete_by_user_id(self, user_id: int) -> None:
        token = await self.get_by_user_id(user_id)
        if token:
            await self.db.delete(token)
            await self.db.commit()

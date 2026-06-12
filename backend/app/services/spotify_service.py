import asyncio
from datetime import datetime, timedelta, timezone

import httpx
from fastapi import HTTPException
from loguru import logger

from app.core.config import require_spotify_credentials


class SpotifyService:
    def __init__(self):
        self._token: str | None = None
        self._token_expires_at: datetime | None = None
        self._lock = asyncio.Lock()

    async def _get_app_token(self) -> str:
        now = datetime.now(timezone.utc)
        if self._token and self._token_expires_at and now < self._token_expires_at:
            logger.debug("Using cached Spotify token")
            return self._token

        async with self._lock:
            now = datetime.now(timezone.utc)
            if self._token and self._token_expires_at and now < self._token_expires_at:
                logger.debug("Using cached Spotify token (after lock)")
                return self._token

            try:
                client_id, client_secret = require_spotify_credentials()
            except ValueError:
                raise HTTPException(
                    status_code=503, detail="Spotify integration not configured"
                )

            logger.info("Fetching new Spotify app token")
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        "https://accounts.spotify.com/api/token",
                        data={"grant_type": "client_credentials"},
                        auth=(client_id, client_secret),
                    )
                    response.raise_for_status()
                except httpx.HTTPError as e:
                    logger.error("Failed to fetch Spotify app token: {}", str(e))
                    raise HTTPException(
                        status_code=502, detail="Spotify authentication failed"
                    )

            try:
                data = response.json()
                self._token = data["access_token"]
                expires_in = int(data["expires_in"])
            except (ValueError, KeyError, TypeError) as e:
                logger.error("Unexpected Spotify token response: {}", str(e))
                raise HTTPException(
                    status_code=502, detail="Spotify authentication failed"
                )
            self._token_expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=max(expires_in - 60, 0)
            )
            logger.info("Spotify token fetched and cached")
            return self._token

    async def search_tracks(self, query: str) -> list[dict]:
        token = await self._get_app_token()

        logger.debug("Searching Spotify for: {}", query)
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://api.spotify.com/v1/search",
                    params={"q": query, "type": "track", "limit": 10},
                    headers={"Authorization": f"Bearer {token}"},
                )
                response.raise_for_status()
            except httpx.HTTPError as e:
                logger.error("Spotify search failed: {}", str(e))
                raise HTTPException(
                    status_code=502, detail="Spotify search unavailable"
                )

        try:
            data = response.json()
            items = data["tracks"]["items"]
        except (ValueError, KeyError, TypeError) as e:
            logger.error("Unexpected Spotify search response: {}", str(e))
            raise HTTPException(status_code=502, detail="Spotify search unavailable")
        tracks = []
        for item in items:
            tracks.append(
                {
                    "spotify_track_id": item["id"],
                    "title": item["name"],
                    "artist": item["artists"][0]["name"],
                    "album": item["album"]["name"],
                    "duration_seconds": item["duration_ms"] // 1000,
                    "preview_url": item.get("preview_url"),
                }
            )

        logger.debug("Found {} tracks for query: {}", len(tracks), query)
        return tracks


spotify_service = SpotifyService()

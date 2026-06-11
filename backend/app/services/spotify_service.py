from datetime import datetime, timedelta, timezone

import httpx
from loguru import logger

from app.core.config import settings


class SpotifyService:
    def __init__(self):
        self._token: str | None = None
        self._token_expires_at: datetime | None = None

    async def _get_app_token(self) -> str:
        now = datetime.now(timezone.utc)
        if self._token and self._token_expires_at and now < self._token_expires_at:
            logger.debug("Using cached Spotify token")
            return self._token

        logger.info("Fetching new Spotify app token")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://accounts.spotify.com/api/token",
                data={"grant_type": "client_credentials"},
                auth=(settings.spotify_client_id, settings.spotify_client_secret),
            )
            response.raise_for_status()
            data = response.json()

        self._token = data["access_token"]
        self._token_expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=data["expires_in"] - 60
        )
        logger.info("Spotify token fetched and cached")
        return self._token

    async def search_tracks(self, query: str) -> list[dict]:
        token = await self._get_app_token()

        logger.info(f"Searching Spotify for: {query}")
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.spotify.com/v1/search",
                params={"q": query, "type": "track", "limit": 10},
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            data = response.json()

        tracks = []
        for item in data["tracks"]["items"]:
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

        # DEBUG
        print(f"Found {len(tracks)} tracks for query: {query}")
        return tracks


spotify_service = SpotifyService()

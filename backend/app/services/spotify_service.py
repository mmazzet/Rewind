import asyncio
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
from loguru import logger

from app.core.config import require_spotify_credentials, settings
from app.core.exceptions import (
    NotAuthorisedError,
    SpotifyNotConfiguredError,
    SpotifyNotConnectedError,
    SpotifyOAuthError,
    SpotifyUnavailableError,
    TapeNotFoundError,
)
from app.repositories.spotify_token_repository import SpotifyTokenRepository
from app.repositories.tape_repository import TapeRepository


class SpotifyClient:
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
                raise SpotifyNotConfiguredError("Spotify integration not configured")

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
                    raise SpotifyUnavailableError("Spotify authentication failed")

            try:
                data = response.json()
                self._token = data["access_token"]
                expires_in = int(data["expires_in"])
            except (ValueError, KeyError, TypeError) as e:
                logger.error("Unexpected Spotify token response: {}", str(e))
                raise SpotifyUnavailableError("Spotify authentication failed")

            self._token_expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=max(expires_in - 60, 0)
            )
            logger.info("Spotify token fetched and cached")
            return self._token

    async def search(self, query: str) -> dict:
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
                raise SpotifyUnavailableError("Spotify search unavailable")

        return response.json()

    def get_auth_url(self) -> str:
        """Return the Spotify OAuth consent screen URL."""
        client_id, _ = require_spotify_credentials()
        params = {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": settings.spotify_redirect_uri,
            "scope": "playlist-modify-public playlist-modify-private",
            "show_dialog": "true",
        }
        return f"https://accounts.spotify.com/authorize?{urlencode(params)}"

    async def exchange_code_for_tokens(self, code: str) -> dict:
        """Exchange an OAuth auth code for access and refresh tokens."""
        client_id, client_secret = require_spotify_credentials()

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://accounts.spotify.com/api/token",
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": settings.spotify_redirect_uri,
                    },
                    auth=(client_id, client_secret),
                )
                response.raise_for_status()
            except httpx.HTTPError as e:
                logger.error("Spotify token exchange failed: {}", str(e))
                raise SpotifyOAuthError("Failed to exchange Spotify auth code")

        try:
            data = response.json()
            logger.debug("Spotify token response scopes: {}", data.get("scope"))
            return {
                "access_token": data["access_token"],
                "refresh_token": data.get("refresh_token"),
                "expires_in": int(data["expires_in"]),
            }
        except (KeyError, TypeError) as e:
            logger.error("Unexpected Spotify token exchange response: {}", str(e))
            raise SpotifyOAuthError("Failed to exchange Spotify auth code")

    async def create_playlist(
        self, access_token: str, title: str, track_ids: list[str]
    ) -> str:
        """Create a private Spotify playlist and return its URL."""
        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient() as client:
            try:
                # Create the playlist
                response = await client.post(
                    "https://api.spotify.com/v1/me/playlists",
                    json={"name": title, "public": False},
                    headers=headers,
                )

                response.raise_for_status()
                playlist = response.json()
                playlist_id = playlist["id"]
                playlist_url = playlist["external_urls"]["spotify"]

                # Add tracks
                track_uris = [f"spotify:track:{tid}" for tid in track_ids]
                tracks_response = await client.post(
                    f"https://api.spotify.com/v1/playlists/{playlist_id}/items",
                    json={"uris": track_uris},
                    headers=headers,
                )

                tracks_response.raise_for_status()
            except httpx.HTTPError as e:
                logger.error("Spotify playlist creation failed: {}", str(e))
                raise SpotifyUnavailableError("Failed to create Spotify playlist")

        return playlist_url


class SpotifyService:
    def __init__(self, client: SpotifyClient):
        self.client = client

    async def search_tracks(self, query: str) -> list[dict]:
        data = await self.client.search(query)

        try:
            items = data["tracks"]["items"]
        except (KeyError, TypeError) as e:
            logger.error("Unexpected Spotify search response: {}", str(e))
            raise SpotifyUnavailableError("Spotify search unavailable")

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

    def get_auth_url(self) -> str:
        """Return the Spotify OAuth consent screen URL."""
        return self.client.get_auth_url()

    async def handle_oauth_callback(
        self,
        code: str,
        user_id: int,
        token_repo: SpotifyTokenRepository,
    ) -> None:
        """Exchange auth code for tokens and store them."""
        tokens = await self.client.exchange_code_for_tokens(code)

        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=tokens["expires_in"]
        )

        await token_repo.upsert(
            user_id=user_id,
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            expires_at=expires_at,
        )
        logger.info("Spotify tokens stored for user {}", user_id)

    async def export_tape_to_spotify(
        self,
        tape_id: int,
        user_id: int,
        token_repo: SpotifyTokenRepository,
        tape_repo: TapeRepository,
    ) -> str:
        """Create a Spotify playlist from a tape and return the playlist URL."""
        tape = await tape_repo.get_by_id(tape_id)
        if not tape:
            raise TapeNotFoundError("Tape not found")
        if tape.sender_id != user_id:
            raise NotAuthorisedError("Not authorised")

        token = await token_repo.get_by_user_id(user_id)
        if not token:
            raise SpotifyNotConnectedError("Spotify account not connected")

        track_ids = [t.spotify_track_id for t in tape.tracks]

        playlist_url = await self.client.create_playlist(
            access_token=token.access_token,
            title=tape.title,
            track_ids=track_ids,
        )

        await tape_repo.set_spotify_playlist_url(tape, playlist_url)

        logger.info("Spotify playlist created for tape {}", tape_id)
        return playlist_url

    async def _get_spotify_user_id(self, access_token: str) -> str:
        """Fetch the Spotify user ID for the connected account."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://api.spotify.com/v1/me",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                response.raise_for_status()
                return response.json()["id"]
            except httpx.HTTPError as e:
                logger.error("Failed to fetch Spotify user ID: {}", str(e))
                raise SpotifyUnavailableError("Failed to fetch Spotify user profile")


spotify_service = SpotifyService(client=SpotifyClient())

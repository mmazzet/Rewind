"""Shared test doubles used by both unit and integration tests."""


class FakeSpotifyClient:
    """Fake SpotifyClient that returns canned data instead of calling Spotify.

    Used by both unit and integration tests. Every method returns the same
    fixed data, so tests never need real Spotify credentials.

    search() echoes the query back in the track title ("Mock result for
    {query}"). This lets integration tests verify the query parameter really
    reaches the client. For unit tests that need different data, override the
    method per test with an AsyncMock.
    """

    async def search(self, query: str) -> dict:
        return {
            "tracks": {
                "items": [
                    {
                        "id": "mock_1",
                        "name": f"Mock result for {query}",
                        "artists": [{"name": "Mock Artist"}],
                        "album": {"name": "Mock Album"},
                        "duration_ms": 200000,
                        "preview_url": None,
                    }
                ]
            }
        }

    def get_auth_url(self) -> str:
        return "https://accounts.spotify.com/authorize?client_id=fake"

    async def exchange_code_for_tokens(self, code: str) -> dict:
        return {
            "access_token": "fake_access_token",
            "refresh_token": "fake_refresh_token",
            "expires_in": 3600,
        }

    async def create_playlist(
        self, access_token: str, title: str, track_ids: list[str]
    ) -> str:
        return "https://open.spotify.com/playlist/fake123"

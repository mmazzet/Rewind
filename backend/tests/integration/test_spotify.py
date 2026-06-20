from httpx import AsyncClient

from tests.integration.test_tapes import register_and_login

# --- GET /api/v1/spotify/search ---


async def test_search_tracks_authenticated(client: AsyncClient):
    await register_and_login(client)

    response = await client.get("/api/v1/spotify/search", params={"q": "beatles"})

    assert response.status_code == 200
    data = response.json()
    assert len(data["tracks"]) == 1
    assert data["tracks"][0]["title"] == "Mock result for beatles"


async def test_search_tracks_not_authenticated(client: AsyncClient):
    response = await client.get("/api/v1/spotify/search", params={"q": "beatles"})

    assert response.status_code == 401

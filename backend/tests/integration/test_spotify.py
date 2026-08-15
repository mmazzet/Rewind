from httpx import ASGITransport, AsyncClient

from app.main import app
from tests.integration.helpers import (
    helper_send_tape,
    register_and_login,
)

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


# --- GET /api/v1/spotify/auth ---


async def test_spotify_auth_redirects_to_spotify(client: AsyncClient):
    await register_and_login(client)

    # follow_redirects=False so we can inspect the redirect URL
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        cookies=client.cookies,
        follow_redirects=False,
    ) as no_redirect_client:
        response = await no_redirect_client.get("/api/v1/spotify/auth")

    assert response.status_code == 307
    assert response.headers["location"].startswith(
        "https://accounts.spotify.com/authorize"
    )


async def test_spotify_auth_not_authenticated(client: AsyncClient):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=False,
    ) as no_redirect_client:
        response = await no_redirect_client.get("/api/v1/spotify/auth")

    assert response.status_code == 401


# --- GET /api/v1/spotify/callback ---


async def test_spotify_callback_success_redirects(client: AsyncClient):
    await register_and_login(client)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        cookies=client.cookies,
        follow_redirects=False,
    ) as no_redirect_client:
        response = await no_redirect_client.get(
            "/api/v1/spotify/callback",
            params={"code": "valid_auth_code"},
        )

    assert response.status_code == 307
    assert "spotify=connected" in response.headers["location"]


async def test_spotify_callback_user_denied_redirects(client: AsyncClient):
    await register_and_login(client)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        cookies=client.cookies,
        follow_redirects=False,
    ) as no_redirect_client:
        response = await no_redirect_client.get(
            "/api/v1/spotify/callback",
            params={"error": "access_denied"},
        )

    assert response.status_code == 307
    assert "spotify=denied" in response.headers["location"]


async def test_spotify_callback_no_code_redirects(client: AsyncClient):
    await register_and_login(client)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        cookies=client.cookies,
        follow_redirects=False,
    ) as no_redirect_client:
        response = await no_redirect_client.get("/api/v1/spotify/callback")

    assert response.status_code == 307
    assert "spotify=denied" in response.headers["location"]


# --- POST /api/v1/spotify/export/{tape_id} ---


async def test_export_tape_success(client: AsyncClient):
    await register_and_login(client)

    # Connect Spotify first via callback
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        cookies=client.cookies,
        follow_redirects=False,
    ) as no_redirect_client:
        await no_redirect_client.get(
            "/api/v1/spotify/callback",
            params={"code": "valid_auth_code"},
        )

    sent = await helper_send_tape(client)

    response = await client.post(f"/api/v1/spotify/export/{sent['id']}")

    assert response.status_code == 200
    assert (
        response.json()["spotify_playlist_url"]
        == "https://open.spotify.com/playlist/fake123"
    )


async def test_export_tape_not_authenticated(client: AsyncClient):
    response = await client.post("/api/v1/spotify/export/1")

    assert response.status_code == 401


async def test_export_tape_not_found(client: AsyncClient):
    await register_and_login(client)

    response = await client.post("/api/v1/spotify/export/999999")

    assert response.status_code == 404
    assert response.json()["message"] == "Tape not found"


async def test_export_tape_spotify_not_connected(client: AsyncClient):
    await register_and_login(client)
    sent = await helper_send_tape(client)

    # No Spotify token stored — skip the callback step
    response = await client.post(f"/api/v1/spotify/export/{sent['id']}")

    assert response.status_code == 400
    assert response.json()["message"] == "Spotify account not connected"


async def test_export_tape_wrong_user(client: AsyncClient):
    # User 1 creates and sends a tape
    await register_and_login(client, email="user1@example.com")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        cookies=client.cookies,
        follow_redirects=False,
    ) as no_redirect_client:
        await no_redirect_client.get(
            "/api/v1/spotify/callback",
            params={"code": "valid_auth_code"},
        )

    sent = await helper_send_tape(client)

    # User 2 logs in and tries to export user 1's tape
    await client.post("/api/v1/auth/logout")
    await register_and_login(client, email="user2@example.com")

    response = await client.post(f"/api/v1/spotify/export/{sent['id']}")

    assert response.status_code == 403
    assert response.json()["message"] == "Not authorised"

from httpx import AsyncClient


async def register_and_login(
    client: AsyncClient,
    email: str = "test@example.com",
    password: str = "Password123",
):
    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200

    csrf_token = client.cookies.get("csrf_token")
    assert csrf_token is not None, "CSRF token cookie not set after login"
    client.headers["X-CSRF-Token"] = csrf_token


async def create_tape(client: AsyncClient) -> dict:
    response = await client.post(
        "/api/v1/tapes",
        json={"title": "My Mix", "cassette_style": "classic", "length_minutes": 60},
    )
    assert response.status_code == 201
    return response.json()


async def create_track(client: AsyncClient, tape_id: int) -> dict:
    response = await client.post(
        f"/api/v1/tapes/{tape_id}/tracks",
        json={
            "spotify_track_id": "4uLU6hMCjMI75M1A2tKUQC",
            "title": "Come Together",
            "artist": "The Beatles",
            "duration_seconds": 259,
            "side": "A",
            "position": 1,
        },
    )
    assert response.status_code == 201
    return response.json()


async def mark_tape_ready(client: AsyncClient, tape_id: int) -> dict:
    response = await client.patch(f"/api/v1/tapes/{tape_id}/ready")
    assert response.status_code == 200
    return response.json()


async def helper_send_tape(client: AsyncClient) -> dict:
    tape = await create_tape(client)
    await create_track(client, tape["id"])
    await mark_tape_ready(client, tape["id"])
    response = await client.post(
        f"/api/v1/tapes/{tape['id']}/send",
        json={"recipient_email": "friend@example.com", "message": "Enjoy!"},
    )
    assert response.status_code == 200
    return response.json()

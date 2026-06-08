from httpx import AsyncClient

# --- Helper ---


async def register_and_login(
    client: AsyncClient,
    email: str = "test@example.com",
    password: str = "Password123",
):
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    # Extract CSRF token and add to headers for protected endpoints
    csrf_token = client.cookies.get("csrf_token")
    if csrf_token:
        client.headers["X-CSRF-Token"] = csrf_token


async def create_tape(client: AsyncClient) -> dict:
    response = await client.post(
        "/api/v1/tapes",
        json={"title": "My Mix", "cassette_style": "classic", "length_minutes": 60},
    )
    return response.json()


# --- POST /api/v1/tapes ---


async def test_create_tape_success(client):
    await register_and_login(client)
    response = await client.post(
        "/api/v1/tapes",
        json={"title": "My Mix", "cassette_style": "classic", "length_minutes": 60},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My Mix"
    assert data["cassette_style"] == "classic"
    assert data["length_minutes"] == 60
    assert data["status"] == "draft"


async def test_create_tape_not_authenticated(client):

    response = await client.post(
        "/api/v1/tapes",
        json={"title": "My Mix", "cassette_style": "classic", "length_minutes": 60},
    )
    assert response.status_code == 401


async def test_create_tape_invalid_style(client):
    await register_and_login(client)
    response = await client.post(
        "/api/v1/tapes",
        json={
            "title": "My Mix",
            "cassette_style": "invalid_style",
            "length_minutes": 60,
        },
    )
    assert response.status_code == 422


async def test_create_tape_title_too_long(client):
    await register_and_login(client)
    response = await client.post(
        "/api/v1/tapes",
        json={"title": "x" * 101, "cassette_style": "classic", "length_minutes": 60},
    )
    assert response.status_code == 422


async def test_create_tape_invalid_length(client):
    await register_and_login(client)
    response = await client.post(
        "/api/v1/tapes",
        json={"title": "My Mix", "cassette_style": "classic", "length_minutes": 45},
    )
    assert response.status_code == 422


# --- GET /api/v1/tapes/{tape_id} ---


async def test_get_tape_success(client):
    await register_and_login(client)
    tape = await create_tape(client)
    response = await client.get(f"/api/v1/tapes/{tape['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == tape["id"]


async def test_get_tape_not_found(client):
    await register_and_login(client)
    response = await client.get("/api/v1/tapes/999")
    assert response.status_code == 404


async def test_get_tape_wrong_user(client):
    # User 1 creates a tape
    await register_and_login(client, email="user1@example.com")
    tape = await create_tape(client)

    # User 2 tries to fetch it
    await client.post("/api/v1/auth/logout")
    await register_and_login(client, email="user2@example.com")
    response = await client.get(f"/api/v1/tapes/{tape['id']}")
    assert response.status_code == 403

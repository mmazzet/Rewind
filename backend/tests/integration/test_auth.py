from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

TEST_DATABASE_URL = "postgresql+asyncpg://rewind:rewind@db:5432/rewind_test"
_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestSessionLocal = sessionmaker(
    bind=_engine, class_=AsyncSession, expire_on_commit=False
)


async def test_register_success(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "Password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password_hash" not in data


async def test_register_existing_email(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "Password123"},
    )
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "Password123"},
    )
    assert response.status_code == 409
    data = response.json()
    assert data["message"] == "Email already registered"


async def test_register_short_password(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "123"},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["message"] == "Password must be at least 8 characters"


async def test_login_success(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "Password123"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "Password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password_hash" not in data


async def test_login_wrong_password(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "Password123"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "WrongPassword123"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["message"] == "Invalid credentials"


async def test_login_nonexistent_email(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "Password123"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["message"] == "Invalid credentials"


async def test_get_current_user_success(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "Password123"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "Password123"},
    )

    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 200


async def test_get_current_user_without_cookie(client):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_logout(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "Password123"},
    )
    await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "Password123"},
    )
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 204
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_verify_email_success(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "Password123"},
    )

    async with TestSessionLocal() as session:
        result = await session.execute(
            text(
                "SELECT verification_token FROM users WHERE email = 'test@example.com'"
            )
        )
        token = result.scalar_one()

    response = await client.post(
        "/api/v1/auth/verify-email",
        json={"token": token},
    )

    assert response.status_code == 200
    data = response.json()
    print("DEBUG response:", data)  # DEBUG
    assert data["message"] == "Email verified"


async def test_verify_email_invalid_token(client):
    response = await client.post(
        "/api/v1/auth/verify-email",
        json={"token": "not-a-real-token"},
    )

    assert response.status_code == 400
    data = response.json()
    assert data["message"] == "Invalid or expired verification token"


async def test_verify_email_claims_tapes(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "sender@example.com", "password": "Password123"},
    )
    await client.post(
        "/api/v1/auth/login",
        json={"email": "sender@example.com", "password": "Password123"},
    )

    # read the CSRF token from the cookie and send it as a header
    csrf_token = client.cookies.get("csrf_token")

    tape_response = await client.post(
        "/api/v1/tapes",
        json={
            "title": "Mix for Maria",
            "cassette_style": "classic",
            "length_minutes": 60,
        },
        headers={"X-CSRF-Token": csrf_token},
    )
    tape_id = tape_response.json()["id"]

    await client.post(
        f"/api/v1/tapes/{tape_id}/tracks",
        json={
            "spotify_track_id": "abc123",
            "title": "Song A",
            "artist": "Artist A",
            "duration_seconds": 200,
            "side": "A",
            "position": 1,
        },
        headers={"X-CSRF-Token": csrf_token},
    )
    await client.patch(
        f"/api/v1/tapes/{tape_id}/ready",
        headers={"X-CSRF-Token": csrf_token},
    )
    await client.post(
        f"/api/v1/tapes/{tape_id}/send",
        json={"recipient_email": "maria@example.com", "message": "For you"},
        headers={"X-CSRF-Token": csrf_token},
    )
    await client.post("/api/v1/auth/logout")

    await client.post(
        "/api/v1/auth/register",
        json={"email": "maria@example.com", "password": "Password123"},
    )

    async with TestSessionLocal() as session:
        result = await session.execute(
            text(
                "SELECT verification_token FROM users WHERE email = 'maria@example.com'"
            )
        )
        token = result.scalar_one()

    await client.post(
        "/api/v1/auth/verify-email",
        json={"token": token},
    )

    csrf_token = client.cookies.get("csrf_token")
    await client.post(
        "/api/v1/auth/login",
        json={"email": "maria@example.com", "password": "Password123"},
    )
    csrf_token = client.cookies.get("csrf_token")

    inbox_response = await client.get("/api/v1/tapes/received")
    assert inbox_response.status_code == 200
    tapes = inbox_response.json()
    assert len(tapes) == 1
    assert tapes[0]["title"] == "Mix for Maria"

from httpx import AsyncClient

from app.core.exceptions import EmailDeliveryError

# --- Helper ---


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


async def test_send_tape_success(client: AsyncClient):
    await register_and_login(client)
    tape = await create_tape(client)
    await create_track(client, tape["id"])
    await mark_tape_ready(client, tape["id"])

    response = await client.post(
        f"/api/v1/tapes/{tape['id']}/send",
        json={"recipient_email": "friend@example.com", "message": "Enjoy!"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "sent"
    assert data["public_token"] is not None
    assert data["sent_at"] is not None


async def test_send_tape_not_authenticated(client: AsyncClient):
    await register_and_login(client)
    tape = await create_tape(client)
    await create_track(client, tape["id"])
    await mark_tape_ready(client, tape["id"])

    client.cookies.clear()

    response = await client.post(
        f"/api/v1/tapes/{tape['id']}/send",
        json={"recipient_email": "friend@example.com", "message": "Enjoy!"},
    )

    assert response.status_code == 401
    assert response.json()["message"] == "Not authenticated"


async def test_send_tape_wrong_user(client: AsyncClient):
    await register_and_login(client)
    tape = await create_tape(client)
    await create_track(client, tape["id"])
    await mark_tape_ready(client, tape["id"])

    client.cookies.clear()
    await register_and_login(client, email="user2@example.com", password="password2")

    response = await client.post(
        f"/api/v1/tapes/{tape['id']}/send",
        json={"recipient_email": "friend@example.com", "message": "Enjoy!"},
    )

    assert response.status_code == 403
    assert response.json()["message"] == "Not authorised"


async def test_send_tape_not_ready(client: AsyncClient):
    await register_and_login(client)
    tape = await create_tape(client)
    await create_track(client, tape["id"])
    # deliberately skip mark_tape_ready — tape is still "draft"

    response = await client.post(
        f"/api/v1/tapes/{tape['id']}/send",
        json={"recipient_email": "friend@example.com", "message": "Enjoy!"},
    )

    assert response.status_code == 409
    assert response.json()["message"] == "Tape must be in ready status to send"


async def test_send_tape_already_sent(client: AsyncClient):
    await register_and_login(client)
    tape = await create_tape(client)
    await create_track(client, tape["id"])
    await mark_tape_ready(client, tape["id"])

    first_response = await client.post(
        f"/api/v1/tapes/{tape['id']}/send",
        json={"recipient_email": "friend@example.com", "message": "Enjoy!"},
    )
    assert first_response.status_code == 200

    second_response = await client.post(
        f"/api/v1/tapes/{tape['id']}/send",
        json={"recipient_email": "friend@example.com", "message": "Enjoy!"},
    )

    assert second_response.status_code == 409
    assert second_response.json()["message"] == "Tape must be in ready status to send"


async def test_send_tape_missing_recipient_email(client: AsyncClient):
    await register_and_login(client)
    tape = await create_tape(client)

    response = await client.post(
        f"/api/v1/tapes/{tape['id']}/send",
        json={"message": "Enjoy!"},
    )

    assert response.status_code == 422
    assert "recipient_email" in response.json()["details"]


async def test_send_tape_invalid_email_format(client: AsyncClient):
    await register_and_login(client)
    tape = await create_tape(client)

    response = await client.post(
        f"/api/v1/tapes/{tape['id']}/send",
        json={"recipient_email": "not-an-email", "message": "Enjoy!"},
    )

    assert response.status_code == 422
    assert "recipient_email" in response.json()["details"]


async def test_send_tape_message_too_long(client: AsyncClient):
    await register_and_login(client)
    tape = await create_tape(client)

    response = await client.post(
        f"/api/v1/tapes/{tape['id']}/send",
        json={"recipient_email": "friend@example.com", "message": "x" * 501},
    )

    assert response.status_code == 422
    assert "message" in response.json()["details"]


async def test_send_tape_not_found(client: AsyncClient):
    await register_and_login(client)

    response = await client.post(
        "/api/v1/tapes/999999/send",
        json={"recipient_email": "friend@example.com", "message": "Enjoy!"},
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Tape not found"


async def test_send_tape_email_failure_returns_502(
    client: AsyncClient, fake_email_service
):
    fake_email_service.side_effect = EmailDeliveryError("Could not send tape email")

    await register_and_login(client)
    tape = await create_tape(client)
    await create_track(client, tape["id"])
    await mark_tape_ready(client, tape["id"])

    response = await client.post(
        f"/api/v1/tapes/{tape['id']}/send",
        json={"recipient_email": "friend@example.com", "message": "Enjoy!"},
    )

    assert response.status_code == 502


# --- GET /api/v1/tapes/public/{public_token} ---


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


async def test_get_public_tape_success(client: AsyncClient):
    await register_and_login(client)
    sent = await helper_send_tape(client)

    client.cookies.clear()

    response = await client.get(f"/api/v1/tapes/public/{sent['public_token']}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "sent"
    assert data["title"] == "My Mix"
    assert len(data["tracks"]) == 1
    assert "recipient_email" not in data
    assert "message" not in data


async def test_get_public_tape_not_found(client: AsyncClient):
    response = await client.get("/api/v1/tapes/public/fake-token-123")

    assert response.status_code == 404
    assert response.json()["message"] == "Tape not found"


async def test_get_public_tape_draft_not_accessible(client: AsyncClient):
    await register_and_login(client)
    tape = await create_tape(client)

    response = await client.get(f"/api/v1/tapes/public/{tape['id']}")

    assert response.status_code == 404


# --- GET /api/v1/tapes/sent ---


async def test_get_sent_tapes_empty(client: AsyncClient):
    await register_and_login(client)
    response = await client.get("/api/v1/tapes/sent")
    assert response.status_code == 200
    assert response.json() == []


async def test_get_sent_tapes_returns_sent_tapes(client: AsyncClient):
    await register_and_login(client)
    await helper_send_tape(client)

    response = await client.get("/api/v1/tapes/sent")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "sent"
    assert data[0]["recipient_email"] == "friend@example.com"


async def test_get_sent_tapes_excludes_drafts(client: AsyncClient):
    await register_and_login(client)
    await create_tape(client)  # draft, never sent

    response = await client.get("/api/v1/tapes/sent")
    assert response.status_code == 200
    assert response.json() == []


async def test_get_sent_tapes_not_authenticated(client: AsyncClient):
    response = await client.get("/api/v1/tapes/sent")
    assert response.status_code == 401


async def test_get_sent_tapes_only_returns_own_tapes(client: AsyncClient):
    # User 1 sends a tape
    await register_and_login(client, email="user1@example.com")
    await helper_send_tape(client)

    # User 2 logs in and checks their outbox
    await client.post("/api/v1/auth/logout")
    await register_and_login(client, email="user2@example.com")

    response = await client.get("/api/v1/tapes/sent")
    assert response.status_code == 200
    assert response.json() == []


# --- GET /api/v1/tapes/received ---


async def test_get_received_tapes_empty(client: AsyncClient):
    await register_and_login(client)
    response = await client.get("/api/v1/tapes/received")
    assert response.status_code == 200
    assert response.json() == []


async def test_get_received_tapes_not_authenticated(client: AsyncClient):
    response = await client.get("/api/v1/tapes/received")
    assert response.status_code == 401


async def test_get_received_tapes_returns_claimed_tapes(client: AsyncClient):
    # This tests the query filter — recipient_id must be set.
    # In the current MVP, claiming is not yet implemented, so this stays empty
    # until Phase 7. This test documents that behaviour explicitly.
    await register_and_login(client)
    response = await client.get("/api/v1/tapes/received")
    assert response.status_code == 200
    assert response.json() == []


# --- PATCH /api/v1/tapes/{tape_id}/archive ---


async def test_archive_tape_success(client: AsyncClient):
    await register_and_login(client)
    sent = await helper_send_tape(client)
    tape_id = sent["id"]

    response = await client.patch(f"/api/v1/tapes/{tape_id}/archive")
    assert response.status_code == 200
    assert response.json()["status"] == "archived"


async def test_archive_tape_not_authenticated(client: AsyncClient):
    response = await client.patch("/api/v1/tapes/1/archive")
    assert response.status_code == 401


async def test_archive_tape_not_found(client: AsyncClient):
    await register_and_login(client)
    response = await client.patch("/api/v1/tapes/999999/archive")
    assert response.status_code == 404
    assert response.json()["message"] == "Tape not found"


async def test_archive_tape_wrong_user(client: AsyncClient):
    await register_and_login(client)
    sent = await helper_send_tape(client)
    tape_id = sent["id"]

    await client.post("/api/v1/auth/logout")
    await register_and_login(client, email="user2@example.com")

    response = await client.patch(f"/api/v1/tapes/{tape_id}/archive")
    assert response.status_code == 403
    assert response.json()["message"] == "Not authorised"


async def test_archive_tape_not_sent(client: AsyncClient):
    await register_and_login(client)
    tape = await create_tape(client)  # still draft

    response = await client.patch(f"/api/v1/tapes/{tape['id']}/archive")
    assert response.status_code == 409
    assert response.json()["message"] == "Tape must be in sent status to archive"


async def test_archive_tape_removes_from_sent_list(client: AsyncClient):
    await register_and_login(client)
    sent = await helper_send_tape(client)
    tape_id = sent["id"]

    await client.patch(f"/api/v1/tapes/{tape_id}/archive")

    response = await client.get("/api/v1/tapes/sent")
    assert response.status_code == 200
    assert response.json() == []

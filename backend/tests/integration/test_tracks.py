from httpx import AsyncClient
from sqlalchemy import select

from app.models.tape import Tape, TapeStatus
from app.models.track import Track
from tests.integration.conftest import TestSessionLocal
from tests.integration.test_tapes import create_tape, register_and_login

# --- POST /api/v1/tapes/{tape_id}/tracks ---


async def test_add_track_success(client: AsyncClient):
    await register_and_login(client)
    print("# DEBUG logged in")  # DEBUG

    tape = await create_tape(client)
    print("# DEBUG created tape:", tape)  # DEBUG

    response = await client.post(
        f"/api/v1/tapes/{tape['id']}/tracks",
        json={
            "spotify_track_id": "4uLU6hMCjMI75M1A2tKUQC",
            "title": "Come Together",
            "artist": "The Beatles",
            "duration_seconds": 259,
            "side": "A",
            "position": 1,
        },
    )
    print("# DEBUG status code:", response.status_code)  # DEBUG
    print("# DEBUG response json:", response.json())  # DEBUG

    assert response.status_code == 201
    data = response.json()
    assert data["spotify_track_id"] == "4uLU6hMCjMI75M1A2tKUQC"
    assert data["side"] == "A"
    assert data["position"] == 1


async def test_add_track_tape_not_draft(client: AsyncClient):
    await register_and_login(client)
    tape = await create_tape(client)
    print("# DEBUG tape before status change:", tape)  # DEBUG

    # Force the tape out of draft status directly in the database,
    # since PATCH /ready does not exist yet.
    async with TestSessionLocal() as session:
        result = await session.execute(select(Tape).where(Tape.id == tape["id"]))
        tape_row = result.scalar_one()
        print("# DEBUG tape status before:", tape_row.status)  # DEBUG
        tape_row.status = TapeStatus.sent
        await session.commit()
        print("# DEBUG tape status after:", tape_row.status)  # DEBUG

    response = await client.post(
        f"/api/v1/tapes/{tape['id']}/tracks",
        json={
            "spotify_track_id": "4uLU6hMCjMI75M1A2tKUQC",
            "title": "Come Together",
            "artist": "The Beatles",
            "duration_seconds": 259,
            "side": "A",
            "position": 1,
        },
    )
    print("# DEBUG status code:", response.status_code)  # DEBUG
    print("# DEBUG response json:", response.json())  # DEBUG

    assert response.status_code == 409


async def test_add_track_not_authenticated(client: AsyncClient):
    response = await client.post(
        "/api/v1/tapes/999/tracks",
        json={
            "spotify_track_id": "4uLU6hMCjMI75M1A2tKUQC",
            "title": "Come Together",
            "artist": "The Beatles",
            "duration_seconds": 259,
            "side": "A",
            "position": 1,
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


async def test_add_track_wrong_user(client: AsyncClient):
    # Register and login as user 1
    await register_and_login(client)
    tape = await create_tape(client)

    # Logout user 1 by clearing cookies
    client.cookies.clear()

    # Register and login as user 2
    await register_and_login(client, email="user2@example.com", password="password2")

    response = await client.post(
        f"/api/v1/tapes/{tape['id']}/tracks",
        json={
            "spotify_track_id": "4uLU6hMCjMI75M1A2tKUQC",
            "title": "Helter Skelter",
            "artist": "The Beatles",
            "duration_seconds": 2255,
            "side": "A",
            "position": 1,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorised"


async def test_add_track_tape_not_found(client: AsyncClient):
    await register_and_login(client)

    response = await client.post(
        "/api/v1/tapes/999999/tracks",
        json={
            "spotify_track_id": "abc",
            "title": "Song",
            "artist": "Artist",
            "duration_seconds": 180,
            "side": "A",
            "position": 1,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Tape not found"


async def test_add_track_side_time_limit_exceeded(client: AsyncClient):
    await register_and_login(client)
    tape = await create_tape(client)

    # First track uses almost all available time
    response = await client.post(
        f"/api/v1/tapes/{tape['id']}/tracks",
        json={
            "spotify_track_id": "track1",
            "title": "Long Song",
            "artist": "Artist",
            "duration_seconds": 1700,
            "side": "A",
            "position": 1,
        },
    )

    assert response.status_code == 201

    # This pushes the side over the limit
    response = await client.post(
        f"/api/v1/tapes/{tape['id']}/tracks",
        json={
            "spotify_track_id": "track2",
            "title": "Another Song",
            "artist": "Artist",
            "duration_seconds": 200,
            "side": "A",
            "position": 2,
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Side time limit exceeded"


async def create_track(client: AsyncClient, tape_id: int):
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


async def test_remove_track_success(client: AsyncClient):
    await register_and_login(client)

    tape = await create_tape(client)
    track = await create_track(client, tape["id"])

    response = await client.delete(f"/api/v1/tapes/{tape['id']}/tracks/{track['id']}")

    assert response.status_code in (200, 204)

    async with TestSessionLocal() as session:
        result = await session.execute(select(Track).where(Track.id == track["id"]))

        assert result.scalar_one_or_none() is None


async def test_remove_track_tape_not_found(client: AsyncClient):
    await register_and_login(client)

    response = await client.delete("/api/v1/tapes/999999/tracks/1")

    assert response.status_code == 404
    assert response.json()["detail"] == "Tape not found"


async def test_remove_track_wrong_user(client: AsyncClient):
    # User 1 creates tape and track
    await register_and_login(client)

    tape = await create_tape(client)
    track = await create_track(client, tape["id"])

    client.cookies.clear()

    # User 2 attempts deletion
    await register_and_login(
        client,
        email="user2@example.com",
        password="password2",
    )

    response = await client.delete(f"/api/v1/tapes/{tape['id']}/tracks/{track['id']}")

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorised"


async def test_remove_track_tape_not_draft(client: AsyncClient):
    await register_and_login(client)

    tape = await create_tape(client)
    track = await create_track(client, tape["id"])

    async with TestSessionLocal() as session:
        result = await session.execute(select(Tape).where(Tape.id == tape["id"]))
        tape_row = result.scalar_one()

        tape_row.status = TapeStatus.sent
        await session.commit()

    response = await client.delete(f"/api/v1/tapes/{tape['id']}/tracks/{track['id']}")

    assert response.status_code == 409
    assert response.json()["detail"] == "Tape is not in draft status"


async def test_remove_track_not_authenticated(client: AsyncClient):
    await register_and_login(client)

    tape = await create_tape(client)
    track = await create_track(client, tape["id"])

    client.cookies.clear()

    response = await client.delete(f"/api/v1/tapes/{tape['id']}/tracks/{track['id']}")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

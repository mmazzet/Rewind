from unittest.mock import AsyncMock, patch

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.db.session import Base, get_db
from app.main import app
from app.services.spotify_service import spotify_service

TEST_DATABASE_URL = "postgresql+asyncpg://rewind:rewind@db:5432/rewind_test"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


class FakeSpotifyClient:
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


@pytest_asyncio.fixture(autouse=True)
async def fake_spotify_client():
    real_client = spotify_service.client
    spotify_service.client = FakeSpotifyClient()
    yield
    spotify_service.client = real_client


@pytest_asyncio.fixture(autouse=True)
async def fake_email_service():
    with patch(
        "app.services.tape_service.email_service.send_tape_email",
        new_callable=AsyncMock,
    ) as mock_send:
        yield mock_send

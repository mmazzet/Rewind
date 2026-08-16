from unittest.mock import AsyncMock, patch

import pytest_asyncio
from argon2 import PasswordHasher
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.db.session import Base, get_db
from app.main import app
from app.services.spotify_service import spotify_service
from tests.fakes import FakeSpotifyClient

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


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(autouse=True)
async def truncate_tables(setup_database):
    table_names = ", ".join(table.name for table in Base.metadata.sorted_tables)
    async with test_engine.begin() as conn:
        await conn.execute(
            text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE")
        )
    yield


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


@pytest_asyncio.fixture(autouse=True)
async def fake_spotify_client():
    real_client = spotify_service.client
    spotify_service.client = FakeSpotifyClient()
    yield
    spotify_service.client = real_client


@pytest_asyncio.fixture(autouse=True)
async def fake_email_service():
    with (
        patch(
            "app.services.tape_service.email_service.send_tape_email",
            new_callable=AsyncMock,
        ) as mock_send_tape,
        patch(
            "app.routers.auth.email_service.send_verification_email",
            new_callable=AsyncMock,
        ),
    ):
        yield mock_send_tape


@pytest_asyncio.fixture(autouse=True)
async def fast_password_hasher():
    fast_ph = PasswordHasher(time_cost=1, memory_cost=8, parallelism=1)
    with patch("app.services.auth_service.ph", new=fast_ph):
        yield

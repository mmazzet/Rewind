from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from argon2.exceptions import VerifyMismatchError

from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    PasswordTooShortError,
)
from app.services import auth_service


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def existing_user():
    user = MagicMock()
    user.id = 1
    user.email = "test@example.com"
    user.password_hash = "$argon2id$v=19$m=65536,t=3,p=4$fake"
    return user


@pytest.mark.asyncio
async def test_register_success(mock_db):
    # Arrange: no existing user, create_user returns a new user
    new_user = MagicMock()
    new_user.id = 1
    new_user.email = "new@example.com"

    mock_create = AsyncMock(return_value=new_user)

    with (
        patch(
            "app.services.auth_service.user_repository.get_user_by_email",
            new=AsyncMock(return_value=None),
        ),
        patch("app.services.auth_service.user_repository.create_user", new=mock_create),
    ):

        result = await auth_service.register(mock_db, "new@example.com", "Password123")

    assert result.email == "new@example.com"
    # verify the password was hashed, not stored plain
    call_args = mock_create.call_args
    actual_password_arg = call_args[0][2]  # third positional argument
    assert actual_password_arg != "Password123"
    assert actual_password_arg.startswith("$argon2")


@pytest.mark.asyncio
async def test_register_password_too_short(mock_db):
    with pytest.raises(PasswordTooShortError) as exc_info:
        await auth_service.register(mock_db, "new@example.com", "short")

    assert exc_info.value.message == "Password must be at least 8 characters"


@pytest.mark.asyncio
async def test_register_existing_email(mock_db):
    existing_user = MagicMock()
    existing_user.id = 1
    existing_user.email = "new@example.com"

    with (
        patch(
            "app.services.auth_service.user_repository.get_user_by_email",
            new=AsyncMock(return_value=existing_user),
        ),
        pytest.raises(EmailAlreadyRegisteredError) as exc_info,
    ):

        await auth_service.register(mock_db, "new@example.com", "123Password")

    assert exc_info.value.message == "Email already registered"


@pytest.mark.asyncio
async def test_login_success(mock_db, existing_user):
    mock_ph = MagicMock()
    mock_ph.verify = MagicMock(return_value=True)

    with (
        patch(
            "app.services.auth_service.user_repository.get_user_by_email",
            new=AsyncMock(return_value=existing_user),
        ),
        patch(
            "app.services.auth_service.ph",
            new=mock_ph,
        ),
    ):
        result = await auth_service.login(mock_db, "test@example.com", "Password123")

    assert result.email == "test@example.com"


@pytest.mark.asyncio
async def test_login_wrong_email(mock_db):
    mock_ph = MagicMock()
    mock_ph.verify = MagicMock(return_value=True)
    with (
        patch(
            "app.services.auth_service.user_repository.get_user_by_email",
            new=AsyncMock(return_value=None),
        ),
        patch(
            "app.services.auth_service.ph",
            new=mock_ph,
        ),
        pytest.raises(InvalidCredentialsError) as exc_info,
    ):
        await auth_service.login(mock_db, "wrong@example.com", "Password123")

    assert exc_info.value.message == "Invalid credentials"


@pytest.mark.asyncio
async def test_login_wrong_password(mock_db, existing_user):
    mock_ph = MagicMock()
    mock_ph.verify = MagicMock(side_effect=VerifyMismatchError)

    with (
        patch(
            "app.services.auth_service.user_repository.get_user_by_email",
            new=AsyncMock(return_value=existing_user),
        ),
        patch(
            "app.services.auth_service.ph",
            new=mock_ph,
        ),
        pytest.raises(InvalidCredentialsError) as exc_info,
    ):
        await auth_service.login(mock_db, "test@example.com", "wrongpassword")

    assert exc_info.value.message == "Invalid credentials"

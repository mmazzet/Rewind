import secrets

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidVerificationTokenError,
    PasswordTooShortError,
)
from app.repositories import user_repository

ph = PasswordHasher()


async def register(db: AsyncSession, email: str, password: str, email_service):
    if len(password) < 8:
        raise PasswordTooShortError("Password must be at least 8 characters")

    existing = await user_repository.get_user_by_email(db, email)
    if existing:
        raise EmailAlreadyRegisteredError("Email already registered")

    password_hash = ph.hash(password)
    verification_token = secrets.token_urlsafe(32)

    user = await user_repository.create_user(
        db, email, password_hash, verification_token
    )

    await email_service.send_verification_email(email, verification_token)
    logger.info("Verification email sent to {}", email)

    return user


async def verify_email(db: AsyncSession, token: str, tape_service):
    user = await user_repository.get_user_by_verification_token(db, token)
    if not user:
        raise InvalidVerificationTokenError("Invalid or expired verification token")

    user = await user_repository.mark_user_verified(db, user)
    logger.info("Email verified for user {}", user.id)

    await tape_service.claim_tapes_for_email(db, user)

    return user


async def login(db: AsyncSession, email: str, password: str):
    user = await user_repository.get_user_by_email(db, email)
    if not user:
        raise InvalidCredentialsError("Invalid credentials")

    try:
        ph.verify(user.password_hash, password)
    except VerifyMismatchError:
        logger.warning("Failed login attempt for email: {}", email)
        raise InvalidCredentialsError("Invalid credentials")

    return user


async def get_current_user(db: AsyncSession, user_id: int):
    user = await user_repository.get_user_by_id(db, user_id)
    if not user:
        raise InvalidCredentialsError("User not found")
    return user

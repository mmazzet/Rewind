from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import user_repository

ph = PasswordHasher()


async def register(db: AsyncSession, email: str, password: str):
    if len(password) < 8:
        raise HTTPException(
            status_code=422, detail="Password must be at least 8 characters"
        )
    existing = await user_repository.get_user_by_email(db, email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    password_hash = ph.hash(password)
    user = await user_repository.create_user(db, email, password_hash)
    return user


async def login(db: AsyncSession, email: str, password: str):
    user = await user_repository.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    try:
        ph.verify(user.password_hash, password)
    except VerifyMismatchError:
        logger.warning("Failed login attempt for email: {}", email)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return user


async def get_current_user(db: AsyncSession, user_id: int):
    user = await user_repository.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

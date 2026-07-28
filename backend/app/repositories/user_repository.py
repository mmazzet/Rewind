from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User


async def create_user(
    db: AsyncSession, email: str, password_hash: str, verification_token: str
) -> User:
    new_user = User(
        email=email, password_hash=password_hash, verification_token=verification_token
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_user_by_verification_token(db: AsyncSession, token: str) -> User | None:
    result = await db.execute(select(User).where(User.verification_token == token))
    return result.scalars().first()


async def mark_user_verified(db: AsyncSession, user: User) -> User:
    user.email_verified = True
    user.verification_token = None
    await db.commit()
    await db.refresh(user)
    return user

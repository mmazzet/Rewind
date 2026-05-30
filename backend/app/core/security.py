from datetime import datetime, timedelta, timezone

from fastapi import Cookie, HTTPException, Response
from jose import JWTError, jwt
from loguru import logger

from app.core.config import settings

ALGORITHM = "HS256"


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_expiry_days)
    payload = {"sub": str(user_id), "exp": int(expire.timestamp())}
    token = jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)

    return token


def set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=settings.env == "production",
        samesite="lax",
        max_age=settings.jwt_expiry_days * 24 * 60 * 60,
    )


def clear_auth_cookie(response: Response) -> None:
    response.delete_cookie(key="access_token")


def get_user_id_from_cookie(access_token: str = Cookie(default=None)) -> int:
    if access_token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(access_token, settings.jwt_secret, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
        return user_id
    except JWTError:
        logger.warning("Invalid or expired JWT token")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

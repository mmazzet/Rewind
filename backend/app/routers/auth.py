from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    clear_auth_cookie,
    create_access_token,
    get_user_id_from_cookie,
    set_auth_cookie,
)
from app.db.session import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, UserResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    body: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user = await auth_service.register(db, body.email, body.password)
    token = create_access_token(user.id)
    set_auth_cookie(response, token)
    return user


@router.post("/login", response_model=UserResponse)
async def login(
    body: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)
):
    user = await auth_service.login(db, body.email, body.password)
    token = create_access_token(user.id)
    set_auth_cookie(response, token)
    return user


@router.post("/logout", status_code=204)
async def logout(response: Response):
    clear_auth_cookie(response)


@router.get("/me", response_model=UserResponse)
async def me(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_user_id_from_cookie),
):
    user = await auth_service.get_current_user(db, user_id)
    return user

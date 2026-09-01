from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    clear_auth_cookie,
    clear_csrf_cookie,
    create_access_token,
    generate_csrf_token,
    get_user_id_from_cookie,
    set_auth_cookie,
    set_csrf_cookie,
)
from app.db.session import get_db
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    UserResponse,
    VerifyEmailRequest,
)
from app.services import auth_service, tape_service
from app.services.email_service import email_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    body: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user = await auth_service.register(db, body.email, body.password, email_service)
    token = create_access_token(user.id)
    set_auth_cookie(response, token)
    csrf_token = generate_csrf_token()
    set_csrf_cookie(response, csrf_token)
    return user


@router.post("/login", response_model=UserResponse)
async def login(
    body: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)
):
    user = await auth_service.login(db, body.email, body.password)
    token = create_access_token(user.id)
    set_auth_cookie(response, token)
    csrf_token = generate_csrf_token()
    set_csrf_cookie(response, csrf_token)
    return user


@router.post("/logout", status_code=204)
async def logout(response: Response):
    clear_auth_cookie(response)
    clear_csrf_cookie(response)


@router.get("/me", response_model=UserResponse)
async def me(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_user_id_from_cookie),
):
    user = await auth_service.get_current_user(db, user_id)
    return user


@router.post("/verify-email", response_model=UserResponse)
async def verify_email(
    body: VerifyEmailRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user = await auth_service.verify_email(db, body.token, tape_service)
    token = create_access_token(user.id)
    set_auth_cookie(response, token)
    csrf_token = generate_csrf_token()
    set_csrf_cookie(response, csrf_token)
    return user

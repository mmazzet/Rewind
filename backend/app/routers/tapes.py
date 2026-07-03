from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_user_id_from_cookie
from app.db.session import get_db
from app.schemas.tape import (
    CreateTapeRequest,
    SendTapeRequest,
    SendTapeResponse,
    TapeResponse,
)
from app.services import tape_service

router = APIRouter(prefix="/tapes", tags=["tapes"])


@router.post("", response_model=TapeResponse, status_code=201)
async def create_tape(
    body: CreateTapeRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_user_id_from_cookie),
):
    tape = await tape_service.create_tape(
        db=db,
        title=body.title,
        cassette_style=body.cassette_style,
        length_minutes=body.length_minutes,
        sender_id=user_id,
    )
    return tape


@router.get("/{tape_id}", response_model=TapeResponse)
async def get_tape(
    tape_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_user_id_from_cookie),
):
    tape = await tape_service.get_tape(db=db, tape_id=tape_id, user_id=user_id)
    return tape


@router.patch("/{tape_id}/ready", response_model=TapeResponse)
async def mark_ready(
    tape_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_user_id_from_cookie),
):
    tape = await tape_service.mark_ready(db=db, tape_id=tape_id, user_id=user_id)
    return tape


@router.post("/{tape_id}/send", response_model=SendTapeResponse)
async def send_tape(
    tape_id: int,
    body: SendTapeRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_user_id_from_cookie),
):
    tape = await tape_service.send_tape(
        db=db,
        tape_id=tape_id,
        user_id=user_id,
        recipient_email=body.recipient_email,
        message=body.message,
    )
    return tape

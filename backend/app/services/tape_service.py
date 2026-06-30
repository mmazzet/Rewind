from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    NotAuthorisedError,
    TapeHasNoTracksError,
    TapeNotFoundError,
    TapeNotInDraftError,
)
from app.models.tape import Tape, TapeStatus
from app.repositories.tape_repository import TapeRepository


async def create_tape(
    db: AsyncSession,
    title: str,
    cassette_style: str,
    length_minutes: int,
    sender_id: int,
) -> Tape:
    tape_repository = TapeRepository(db)
    return await tape_repository.create(
        title=title,
        cassette_style=cassette_style,
        length_minutes=length_minutes,
        sender_id=sender_id,
    )


async def get_tape(db: AsyncSession, tape_id: int, user_id: int) -> Tape:
    tape_repository = TapeRepository(db)
    tape = await tape_repository.get_by_id(tape_id)

    if tape is None:
        raise TapeNotFoundError("Tape not found")

    if tape.sender_id != user_id:
        raise NotAuthorisedError("Not authorised")

    return tape


async def mark_ready(db: AsyncSession, tape_id: int, user_id: int) -> Tape:
    tape_repository = TapeRepository(db)
    tape = await tape_repository.get_by_id(tape_id)

    if tape is None:
        raise TapeNotFoundError("Tape not found")

    if tape.sender_id != user_id:
        raise NotAuthorisedError("Not authorised")

    if tape.status != TapeStatus.draft:
        raise TapeNotInDraftError("Tape is not in draft status")

    if len(tape.tracks) == 0:
        raise TapeHasNoTracksError("Tape has no tracks")

    return await tape_repository.update_status(tape, TapeStatus.ready)

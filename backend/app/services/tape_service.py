import uuid

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    NotAuthorisedError,
    TapeHasNoTracksError,
    TapeNotFoundError,
    TapeNotInDraftError,
    TapeNotReadyError,
    TapeNotSentError,
)
from app.models.tape import Tape, TapeStatus
from app.repositories import user_repository
from app.repositories.tape_repository import TapeRepository
from app.services.email_service import email_service


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


async def send_tape(
    db: AsyncSession,
    tape_id: int,
    user_id: int,
    recipient_email: str,
    message: str | None,
) -> Tape:
    tape_repository = TapeRepository(db)
    tape = await tape_repository.get_by_id(tape_id)

    if tape is None:
        raise TapeNotFoundError("Tape not found")

    if tape.sender_id != user_id:
        raise NotAuthorisedError("Not authorised")

    if tape.status != TapeStatus.ready:
        raise TapeNotReadyError("Tape must be in ready status to send")

    public_token = str(uuid.uuid4())

    sent_tape = await tape_repository.send_tape(
        tape=tape,
        recipient_email=recipient_email,
        message=message,
        public_token=public_token,
    )

    await email_service.send_tape_email(
        recipient=recipient_email,
        public_token=public_token,
        message=message,
    )

    # If the recipient already has a verified account, claim the tape immediately.
    recipient = await user_repository.get_user_by_email(db, recipient_email)
    if recipient and recipient.email_verified:
        sent_tape.recipient_id = recipient.id
        sent_tape = await tape_repository.update_status(sent_tape, TapeStatus.claimed)
        logger.info(
            "Tape {} claimed immediately for existing user {}", tape_id, recipient.id
        )

    return sent_tape


async def get_public_tape(db: AsyncSession, public_token: str) -> Tape:
    """Return a sent tape by its public token.

    Raises:
        TapeNotFoundError: If the tape does not exist or has not been sent yet.
    """
    tape_repository = TapeRepository(db)
    tape = await tape_repository.get_by_public_token(public_token)

    if tape is None or tape.status not in (TapeStatus.sent, TapeStatus.claimed):
        raise TapeNotFoundError("Tape not found")

    return tape


async def get_sent_tapes(db: AsyncSession, user_id: int) -> list[Tape]:
    """Return all sent tapes for the current user's outbox"""
    tape_repository = TapeRepository(db)
    return await tape_repository.get_sent_by_user(sender_id=user_id)


async def get_received_tapes(db: AsyncSession, user_id: int) -> list[Tape]:
    """Return all received tapes for the current user's inbox"""
    tape_repository = TapeRepository(db)
    return await tape_repository.get_received_by_user(recipient_id=user_id)


async def archive_tape(db: AsyncSession, tape_id: int, user_id: int) -> Tape:
    """Archive a sent tape. Only the sender can archive.

    Raises:
        TapeNotFoundError: If the tape does not exist.
        NotAuthorisedError: If the user is not the sender.
        TapeNotSentError: If the tape is not in sent status.
    """
    tape_repository = TapeRepository(db)
    tape = await tape_repository.get_by_id(tape_id)

    if tape is None:
        raise TapeNotFoundError("Tape not found")

    if tape.sender_id != user_id:
        raise NotAuthorisedError("Not authorised")

    if tape.status != TapeStatus.sent:
        raise TapeNotSentError("Tape must be in sent status to archive")

    return await tape_repository.update_status(tape, TapeStatus.archived)


async def claim_tapes_for_email(db: AsyncSession, user) -> None:
    """Find all sent tapes addressed to this user's email and claim them.

    Args:
        db: Database session.
        user: The newly verified user.
    """
    tape_repository = TapeRepository(db)
    tapes = await tape_repository.get_by_recipient_email(user.email)

    for tape in tapes:
        tape.recipient_id = user.id
        await tape_repository.update_status(tape, TapeStatus.claimed)

    logger.info("Claimed {} tape(s) for user {}", len(tapes), user.id)

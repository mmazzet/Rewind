from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.tape import Tape, TapeStatus


class TapeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        title: str,
        cassette_style: str,
        length_minutes: int,
        sender_id: int,
    ) -> Tape:
        new_tape = Tape(
            title=title,
            cassette_style=cassette_style,
            length_minutes=length_minutes,
            sender_id=sender_id,
            status=TapeStatus.draft,
        )
        self.db.add(new_tape)
        await self.db.commit()

        return await self.get_by_id(new_tape.id)

    async def get_by_id(self, tape_id: int) -> Tape | None:
        result = await self.db.execute(
            select(Tape).where(Tape.id == tape_id).options(selectinload(Tape.tracks))
        )
        return result.scalars().first()

    async def get_by_sender(self, sender_id: int) -> list[Tape]:
        result = await self.db.execute(
            select(Tape)
            .where(Tape.sender_id == sender_id)
            .options(selectinload(Tape.tracks))
        )
        return list(result.scalars().all())

    async def update_status(self, tape: Tape, status: TapeStatus) -> Tape:
        tape.status = status
        await self.db.commit()
        await self.db.refresh(tape)
        return tape

    async def send_tape(
        self,
        tape: Tape,
        recipient_email: str,
        message: str | None,
        public_token: str,
    ) -> Tape:
        tape.recipient_email = recipient_email
        tape.message = message
        tape.public_token = public_token
        tape.status = TapeStatus.sent
        tape.sent_at = datetime.now(timezone.utc)

        await self.db.commit()

        return await self.get_by_id(tape.id)

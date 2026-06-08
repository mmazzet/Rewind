from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
        await self.db.refresh(new_tape)
        return new_tape

    async def get_by_id(self, tape_id: int) -> Tape | None:
        result = await self.db.execute(select(Tape).where(Tape.id == tape_id))
        return result.scalars().first()

    async def get_by_sender(self, sender_id: int) -> list[Tape]:
        result = await self.db.execute(select(Tape).where(Tape.sender_id == sender_id))
        return list(result.scalars().all())

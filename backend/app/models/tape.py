import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TapeStatus(enum.Enum):
    draft = "draft"
    ready = "ready"
    sent = "sent"
    claimed = "claimed"
    archived = "archived"


class Tape(Base):
    __tablename__ = "tapes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    cassette_style: Mapped[str] = mapped_column(String(50), nullable=False)
    length_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[TapeStatus] = mapped_column(
        Enum(TapeStatus), default=TapeStatus.draft, nullable=False
    )
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    recipient_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    recipient_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    public_token: Mapped[str | None] = mapped_column(
        String(36), unique=True, nullable=True
    )
    spotify_playlist_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

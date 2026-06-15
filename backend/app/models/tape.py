import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.track import Track


class CassetteStyle(str, enum.Enum):
    classic = "classic"
    chrome = "chrome"
    metal = "metal"
    vintage = "vintage"


class TapeStatus(str, enum.Enum):
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
        SAEnum(TapeStatus), default=TapeStatus.draft, nullable=False
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
    tracks: Mapped[list["Track"]] = relationship("Track", back_populates="tape")

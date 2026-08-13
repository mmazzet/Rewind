from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.tape import CassetteStyle, TapeStatus
from app.schemas.track import TrackResponse


class CreateTapeRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    cassette_style: CassetteStyle
    length_minutes: Literal[60, 90]

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Title cannot be blank")
        return stripped


class TapeResponse(BaseModel):
    id: int
    title: str
    cassette_style: CassetteStyle
    length_minutes: int
    status: TapeStatus
    sender_id: int
    tracks: list[TrackResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class SendTapeRequest(BaseModel):
    recipient_email: EmailStr
    message: str | None = Field(default=None, max_length=500)


class SendTapeResponse(BaseModel):
    id: int
    status: TapeStatus
    public_token: str
    sent_at: datetime

    model_config = {"from_attributes": True}


class PublicTapeResponse(BaseModel):
    id: int
    title: str
    cassette_style: str
    length_minutes: int
    status: str
    message: str | None
    tracks: list[TrackResponse]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SentTapeListItem(BaseModel):
    id: int
    title: str
    recipient_email: str
    status: TapeStatus
    sent_at: datetime
    spotify_playlist_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ReceivedTapeListItem(BaseModel):
    id: int
    title: str
    sender_id: int
    message: str | None
    status: TapeStatus
    sent_at: datetime

    model_config = ConfigDict(from_attributes=True)

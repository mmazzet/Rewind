from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.tape import CassetteStyle, TapeStatus


class CreateTapeRequest(BaseModel):
    title: str = Field(max_length=100)
    cassette_style: CassetteStyle
    length_minutes: Literal[60, 90]


class TapeResponse(BaseModel):
    id: int
    title: str
    cassette_style: str
    length_minutes: int
    status: TapeStatus
    sender_id: int
    created_at: datetime

    model_config = {"from_attributes": True}

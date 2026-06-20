from datetime import datetime

from pydantic import BaseModel, Field

from app.models.track import TrackSide


class AddTrackRequest(BaseModel):
    spotify_track_id: str = Field(max_length=100)
    title: str = Field(max_length=255)
    artist: str = Field(max_length=255)
    duration_seconds: int = Field(gt=0)
    side: TrackSide
    position: int = Field(gt=0)


class TrackResponse(BaseModel):
    id: int
    tape_id: int
    spotify_track_id: str
    title: str
    artist: str
    duration_seconds: int
    side: TrackSide
    position: int
    created_at: datetime

    model_config = {"from_attributes": True}

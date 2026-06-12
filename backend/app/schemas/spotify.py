from pydantic import BaseModel


class SpotifyTrack(BaseModel):
    spotify_track_id: str
    title: str
    artist: str
    album: str
    duration_seconds: int
    preview_url: str | None = None


class SpotifySearchResponse(BaseModel):
    tracks: list[SpotifyTrack]

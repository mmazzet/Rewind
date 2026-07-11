export type CassetteStyle = "classic" | "chrome" | "metal" | "vintage";
export type TrackSide = "A" | "B";

export interface CreateTapeRequest {
  title: string;
  cassette_style: CassetteStyle;
  length_minutes: number;
}

export interface Tape {
  id: number;
  title: string;
  cassette_style: CassetteStyle;
  length_minutes: number;
  status: string;
  tracks: Track[];
  created_at: string;
}

export interface Track {
  id: number;
  tape_id: number;
  spotify_track_id: string;
  title: string;
  artist: string;
  duration_seconds: number;
  side: TrackSide;
  position: number;
  created_at: string;
}

export interface SpotifySearchResult {
  spotify_track_id: string;
  title: string;
  artist: string;
  album: string;
  duration_seconds: number;
  preview_url: string | null;
}

export interface AddTrackRequest {
  spotify_track_id: string;
  title: string;
  artist: string;
  duration_seconds: number;
  side: TrackSide;
  position: number;
}

export interface SendTapeRequest {
  recipient_email: string;
  message?: string;
}

export interface SendTapeResponse {
  id: number;
  status: string;
  public_token: string;
  sent_at: string;
}

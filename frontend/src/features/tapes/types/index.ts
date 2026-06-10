export type CassetteStyle = "classic" | "chrome" | "metal" | "vintage";

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
  tracks: unknown[];
  created_at: string;
}

export interface SentTapeListItem {
  id: number;
  title: string;
  recipient_email: string;
  status: "sent" | "claimed" | "archived";
  sent_at: string;
  spotify_playlist_url: string | null;
}

// Pagination removed — backend returns a plain array
export type SentTapesResponse = SentTapeListItem[];

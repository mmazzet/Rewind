export interface ReceivedTapeListItem {
  id: number;
  title: string;
  sender_id: number;
  message: string | null;
  status: "sent" | "claimed";
  sent_at: string;
  public_token: string | null;
  spotify_playlist_url: string | null;
}

export type ReceivedTapesResponse = ReceivedTapeListItem[];

export interface ReceivedTapeListItem {
  id: number;
  title: string;
  sender_id: number;
  status: "sent" | "claimed";
  sent_at: string;
}

export type ReceivedTapesResponse = ReceivedTapeListItem[];

import apiClient from "@/api/client";
import type { SentTapesResponse } from "../types";

export const outboxApi = {
  getSentTapes: async (): Promise<SentTapesResponse> => {
    const response = await apiClient.get<SentTapesResponse>("/tapes/sent");
    return response.data;
  },

  archiveTape: async (tapeId: number): Promise<void> => {
    await apiClient.patch(`/tapes/${tapeId}/archive`);
  },
};

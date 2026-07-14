import apiClient from "@/api/client";
import type { ReceivedTapesResponse } from "../types";

export const inboxApi = {
  getReceivedTapes: async (): Promise<ReceivedTapesResponse> => {
    const response =
      await apiClient.get<ReceivedTapesResponse>("/tapes/received");
    return response.data;
  },
};

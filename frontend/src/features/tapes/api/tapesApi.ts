import apiClient from "@/api/client";
import type { Tape, CreateTapeRequest } from "../types";

export const tapesApi = {
  createTape: async (data: CreateTapeRequest): Promise<Tape> => {
    const response = await apiClient.post<Tape>("/tapes", data);
    return response.data;
  },

  getTape: async (id: number): Promise<Tape> => {
    const response = await apiClient.get<Tape>(`/tapes/${id}`);
    return response.data;
  },
};

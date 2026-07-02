import apiClient from "@/api/client";
import type { Tape, CreateTapeRequest, Track, AddTrackRequest } from "../types";

export const tapesApi = {
  createTape: async (data: CreateTapeRequest): Promise<Tape> => {
    const response = await apiClient.post<Tape>("/tapes", data);
    return response.data;
  },

  getTape: async (id: number): Promise<Tape> => {
    const response = await apiClient.get<Tape>(`/tapes/${id}`);
    return response.data;
  },

  addTrack: async (tapeId: number, data: AddTrackRequest): Promise<Track> => {
    const response = await apiClient.post<Track>(
      `/tapes/${tapeId}/tracks`,
      data,
    );
    return response.data;
  },

  removeTrack: async (tapeId: number, trackId: number): Promise<void> => {
    await apiClient.delete(`/tapes/${tapeId}/tracks/${trackId}`);
  },

  markReady: async (tapeId: number): Promise<Tape> => {
    const response = await apiClient.patch<Tape>(`/tapes/${tapeId}/ready`);
    return response.data;
  },
};

import apiClient from "@/api/client";
import type { SpotifySearchResult } from "../types";

export interface SpotifyExportResponse {
  spotify_playlist_url: string;
}

export const spotifyApi = {
  search: async (query: string): Promise<SpotifySearchResult[]> => {
    const response = await apiClient.get<{ tracks: SpotifySearchResult[] }>(
      "/spotify/search",
      { params: { q: query } },
    );
    return response.data.tracks;
  },

  connectSpotify: async (code: string): Promise<void> => {
    await apiClient.post("/spotify/callback", null, { params: { code } });
  },

  exportToSpotify: async (tapeId: number): Promise<SpotifyExportResponse> => {
    const response = await apiClient.post<SpotifyExportResponse>(
      `/spotify/export/${tapeId}`,
    );
    return response.data;
  },
};

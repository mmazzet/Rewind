import apiClient from "@/api/client";
import type { SpotifySearchResult } from "../types";

export const spotifyApi = {
  search: async (query: string): Promise<SpotifySearchResult[]> => {
    const response = await apiClient.get<{ tracks: SpotifySearchResult[] }>(
      "/spotify/search",
      { params: { q: query } },
    );
    return response.data.tracks;
  },
};

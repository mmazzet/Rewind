import { useState, useEffect } from "react";
import { spotifyApi } from "../api/spotifyApi";
import type { SpotifySearchResult, TrackSide } from "../types";
import { toast } from "react-hot-toast";
import { getErrorMessage } from "@/api/errorMessage";

interface SpotifySearchProps {
  onAddTrack: (track: SpotifySearchResult, side: TrackSide) => void;
}

export function SpotifySearch({ onAddTrack }: SpotifySearchProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SpotifySearchResult[]>([]);

  useEffect(() => {
    if (query.trim() === "") {
      setResults([]);
      return;
    }
    const timeoutId = setTimeout(() => {
      spotifyApi
        .search(query)
        .then((tracks) => {
          setResults(tracks);
        })
        .catch((error) => {
          toast.error(getErrorMessage(error, "Search failed. Try again."));
        });
    }, 300);
    return () => clearTimeout(timeoutId);
  }, [query]);

  return (
    <div className="w-full max-w-md p-8 bg-white rounded-lg shadow">
      <h2 className="text-lg font-bold mb-4">Search Spotify</h2>

      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search for a song"
        className="w-full border rounded px-3 py-2 text-sm"
      />

      <ul className="mt-4 space-y-2">
        {results.map((track) => (
          <li
            key={track.spotify_track_id}
            className="text-sm border-b pb-2 flex items-center justify-between"
          >
            <div>
              <p className="font-medium">{track.title}</p>
              <p className="text-gray-500">{track.artist}</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => onAddTrack(track, "A")}
                className="text-xs bg-blue-600 text-white px-2 py-1 rounded"
              >
                Add A
              </button>
              <button
                onClick={() => onAddTrack(track, "B")}
                className="text-xs bg-blue-600 text-white px-2 py-1 rounded"
              >
                Add B
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

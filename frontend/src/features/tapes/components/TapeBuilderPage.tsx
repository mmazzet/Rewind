import {
  useSuspenseQuery,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { tapesApi } from "../api/tapesApi";
import type { Tape, Track, TrackSide, SpotifySearchResult } from "../types";
import { SpotifySearch } from "./SpotifySearch";
import { TrackList } from "./TrackList";
import { toast } from "react-hot-toast";
import { getErrorMessage } from "@/api/errorMessage";

export function TapeBuilderPage() {
  const { tapeId } = useParams<{ tapeId: string }>();
  const queryClient = useQueryClient();

  const { data: tape } = useSuspenseQuery<Tape>({
    queryKey: ["tape", tapeId],
    queryFn: () => tapesApi.getTape(Number(tapeId)),
  });

  const { mutate: addTrack } = useMutation({
    mutationFn: ({
      track,
      side,
    }: {
      track: SpotifySearchResult;
      side: TrackSide;
    }) => {
      const tracksOnSide = tape.tracks.filter((t) => t.side === side);
      return tapesApi.addTrack(Number(tapeId), {
        spotify_track_id: track.spotify_track_id,
        title: track.title,
        artist: track.artist,
        duration_seconds: track.duration_seconds,
        side,
        position: tracksOnSide.length + 1,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tape", tapeId] });
    },
    onError: (error) => {
      toast.error(getErrorMessage(error, "Failed to add track."));
    },
  });

  const { mutate: removeTrack } = useMutation({
    mutationFn: (trackId: number) =>
      tapesApi.removeTrack(Number(tapeId), trackId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tape", tapeId] });
    },
    onError: (error) => {
      toast.error(getErrorMessage(error, "Failed to remove track."));
    },
  });

  function handleAddTrack(track: SpotifySearchResult, side: TrackSide) {
    addTrack({ track, side });
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 gap-6">
      <div className="w-full max-w-md p-8 bg-white rounded-lg shadow">
        <h1 className="text-2xl font-bold mb-2">{tape.title}</h1>
        <p className="text-sm text-gray-500 mb-1">
          Style: {tape.cassette_style}
        </p>
        <p className="text-sm text-gray-500">
          Length: {tape.length_minutes} minutes
        </p>
        <p className="text-xs text-gray-400 mt-4">Status: {tape.status}</p>
      </div>
      <SpotifySearch onAddTrack={handleAddTrack} />

      <div className="w-full max-w-md p-8 bg-white rounded-lg shadow flex gap-8">
        <TrackList
          tracks={tape.tracks}
          side="A"
          length_minutes={tape.length_minutes}
          onRemoveTrack={removeTrack}
        />
        <TrackList
          tracks={tape.tracks}
          side="B"
          length_minutes={tape.length_minutes}
          onRemoveTrack={removeTrack}
        />
      </div>
    </div>
  );
}

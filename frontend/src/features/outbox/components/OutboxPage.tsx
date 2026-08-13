import React, { useCallback, useEffect } from "react";
import {
  useSuspenseQuery,
  useQueryClient,
  useMutation,
} from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import toast from "react-hot-toast";
import { outboxApi } from "../api/outboxApi";
import { spotifyApi } from "@/features/tapes/api/spotifyApi";
import { getErrorMessage } from "@/api/errorMessage";
import type { SentTapeListItem } from "../types";

const SPOTIFY_AUTH_URL = "/api/v1/spotify/auth";

const OutboxPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [searchParams, setSearchParams] = useSearchParams();

  // Read Spotify OAuth result from query param and show toast once
  useEffect(() => {
    const spotify = searchParams.get("spotify");
    if (spotify === "connected") {
      toast.success("Spotify connected!");
      setSearchParams({}, { replace: true });
    } else if (spotify === "denied") {
      toast.error("Spotify connection cancelled.");
      setSearchParams({}, { replace: true });
    }
  }, [searchParams, setSearchParams]);

  const { data } = useSuspenseQuery({
    queryKey: ["tapes", "sent"],
    queryFn: () => outboxApi.getSentTapes(),
  });

  const archiveMutation = useMutation({
    mutationFn: (tapeId: number) => outboxApi.archiveTape(tapeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tapes", "sent"] });
      toast.success("Tape archived");
    },
    onError: (error) => {
      toast.error(getErrorMessage(error, "Failed to archive tape"));
    },
  });

  const exportMutation = useMutation({
    mutationFn: (tapeId: number) => spotifyApi.exportToSpotify(tapeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tapes", "sent"] });
      toast.success("Playlist created on Spotify!");
    },
    onError: (error) => {
      toast.error(getErrorMessage(error, "Failed to export to Spotify"));
    },
  });

  const handleArchive = useCallback(
    (tapeId: number) => {
      archiveMutation.mutate(tapeId);
    },
    [archiveMutation],
  );

  const handleExport = useCallback(
    (tapeId: number) => {
      exportMutation.mutate(tapeId);
    },
    [exportMutation],
  );

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Sent tapes</h1>

      {data.length === 0 ? (
        <p className="text-gray-500">You have not sent any tapes yet.</p>
      ) : (
        <ul className="flex flex-col gap-4">
          {data.map((tape: SentTapeListItem) => (
            <li
              key={tape.id}
              className="flex items-center justify-between rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
            >
              <div className="flex flex-col gap-1">
                <span className="font-semibold text-gray-900">
                  {tape.title}
                </span>
                <span className="text-sm text-gray-500">
                  To: {tape.recipient_email}
                </span>
                <span className="text-sm text-gray-500">
                  {new Date(tape.sent_at).toLocaleDateString()}
                </span>
                <span className="text-xs font-medium uppercase tracking-wide text-indigo-600">
                  {tape.status}
                </span>

                {/* Spotify section — only shown for sent or claimed tapes */}
                {(tape.status === "sent" || tape.status === "claimed") && (
                  <div className="mt-2">
                    {tape.spotify_playlist_url ? (
                      <a
                        href={tape.spotify_playlist_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-green-600 hover:underline"
                      >
                        Open Spotify playlist
                      </a>
                    ) : (
                      <div className="flex gap-2 flex-wrap">
                        <a
                          href={SPOTIFY_AUTH_URL}
                          className="rounded px-3 py-1 text-sm text-white bg-green-600 hover:bg-green-700 transition-colors"
                        >
                          Connect Spotify
                        </a>
                        <button
                          onClick={() => handleExport(tape.id)}
                          disabled={exportMutation.isPending}
                          className="rounded px-3 py-1 text-sm text-green-700 border border-green-300 hover:bg-green-50 disabled:opacity-50 transition-colors"
                        >
                          {exportMutation.isPending
                            ? "Exporting..."
                            : "Export to Spotify"}
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>

              <button
                onClick={() => handleArchive(tape.id)}
                disabled={archiveMutation.isPending}
                className="ml-4 self-start rounded px-3 py-1 text-sm text-red-600 border border-red-200 hover:bg-red-50 disabled:opacity-50 transition-colors"
              >
                Archive
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default OutboxPage;

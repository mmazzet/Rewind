import { useSuspenseQuery } from "@tanstack/react-query";
import { useParams, Link } from "react-router-dom";
import { tapesApi } from "../api/tapesApi";
import type { Tape, Track } from "../types";

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function SideTrackList({
  tracks,
  side,
}: {
  tracks: Track[];
  side: "A" | "B";
}): React.ReactElement {
  const sideTracks = tracks
    .filter((t) => t.side === side)
    .sort((a, b) => a.position - b.position);

  return (
    <div className="flex flex-col gap-2">
      <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
        Side {side}
      </h2>
      {sideTracks.length === 0 ? (
        <p className="text-sm text-gray-400">No tracks</p>
      ) : (
        <ul className="flex flex-col gap-1">
          {sideTracks.map((track) => (
            <li
              key={track.id}
              className="flex items-center justify-between text-sm text-gray-700"
            >
              <span>
                {track.position}. {track.title}{" "}
                <span className="text-gray-400">— {track.artist}</span>
              </span>
              <span className="text-gray-400 ml-4 shrink-0">
                {formatDuration(track.duration_seconds)}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function PublicTapePage(): React.ReactElement {
  const { token } = useParams<{ token: string }>();

  // token will always be defined here because the route requires it
  const { data: tape } = useSuspenseQuery<Tape>({
    queryKey: ["public-tape", token],
    queryFn: () => tapesApi.getPublicTape(token!),
  });

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center px-4 py-12">
      <div className="w-full max-w-lg flex flex-col gap-6">
        <div className="text-center">
          <p className="text-xs text-gray-400 uppercase tracking-widest mb-1">
            A mixtape for you
          </p>
          <h1 className="text-2xl font-bold text-gray-800">{tape.title}</h1>
          <p className="text-sm text-gray-500 mt-1">
            {tape.length_minutes} min · {tape.cassette_style}
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex flex-col gap-6">
          {tape.message && (
            <p className="text-sm text-gray-600 italic border-b border-gray-100 pb-4">
              "{tape.message}"
            </p>
          )}
          <SideTrackList tracks={tape.tracks} side="A" />
          <hr className="border-gray-100" />
          <SideTrackList tracks={tape.tracks} side="B" />
        </div>

        {tape.spotify_playlist_url && (
          <a
            href={tape.spotify_playlist_url}
            target="_blank"
            rel="noopener noreferrer"
            className="block text-center rounded-lg bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-4 transition-colors"
          >
            Listen on Spotify →
          </a>
        )}

        <div className="text-center">
          <Link
            to="/register"
            className="text-sm text-indigo-600 hover:underline"
          >
            Want to make your own? Create an account →
          </Link>
        </div>
      </div>
    </div>
  );
}

export default PublicTapePage;

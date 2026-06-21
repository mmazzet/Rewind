import type { Track, TrackSide } from "../types";

interface TrackListProps {
  tracks: Track[];
  side: TrackSide;
  length_minutes: number;
  onRemoveTrack: (trackId: number) => void;
}

export function TrackList({
  tracks,
  side,
  length_minutes,
  onRemoveTrack,
}: TrackListProps) {
  const tracksOnSide = tracks
    .filter((track) => track.side === side)
    .sort((a, b) => a.position - b.position);

  const sideLimitSeconds = (length_minutes / 2) * 60;
  const usedSeconds = tracksOnSide.reduce(
    (total, track) => total + track.duration_seconds,
    0,
  );
  const remainingSeconds = sideLimitSeconds - usedSeconds;
  const minutes = Math.floor(remainingSeconds / 60);
  const seconds = remainingSeconds % 60;

  return (
    <div>
      <h2 className="font-bold mb-2">Side {side}</h2>
      <p className="text-xs text-gray-400">
        {minutes}:{seconds.toString().padStart(2, "0")} remaining
      </p>
      {tracksOnSide.length === 0 ? (
        <p className="text-sm text-gray-400">No tracks yet</p>
      ) : (
        <ul>
          {tracksOnSide.map((track) => (
            <li key={track.id} className="text-sm mb-1">
              {track.title} — {track.artist}
              <button
                onClick={() => onRemoveTrack(track.id)}
                className="ml-2 text-red-500 hover:text-red-700"
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

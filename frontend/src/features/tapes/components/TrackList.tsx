import type { Track, TrackSide } from "../types";

function formatDuration(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

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

  return (
    <div>
      <h2 className="font-bold mb-2">Side {side}</h2>
      <p className="text-xs text-gray-400">
        {`${formatDuration(usedSeconds)} / ${formatDuration(sideLimitSeconds)} used · ${formatDuration(remainingSeconds)} remaining`}
      </p>
      {tracksOnSide.length === 0 ? (
        <p className="text-sm text-gray-400">No tracks yet</p>
      ) : (
        <ul>
          {tracksOnSide.map((track) => (
            <li
              key={track.id}
              className="text-sm mb-1 flex items-center justify-between gap-2"
            >
              <span className="min-w-0 break-words">
                {track.title} — {track.artist}
              </span>
              <span className="flex shrink-0 items-center gap-2">
                <span className="text-gray-400">
                  {formatDuration(track.duration_seconds)}
                </span>
                <button
                  onClick={() => onRemoveTrack(track.id)}
                  className="text-red-500 hover:text-red-700"
                >
                  Remove
                </button>
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

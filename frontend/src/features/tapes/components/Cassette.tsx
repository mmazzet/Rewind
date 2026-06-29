import React from "react";
import {
  CASSETTE_THEMES,
  DEFAULT_THEME,
  cassetteStyles,
} from "./Cassette.styles";
import type { CassetteTheme } from "./Cassette.styles";
import type { Track } from "../types";

const MAX_VISIBLE_TRACKS = 10;
const MAX_TITLE_LENGTH = 25;

function truncate(title: string): string {
  if (title.length <= MAX_TITLE_LENGTH) return title;
  return title.slice(0, MAX_TITLE_LENGTH) + "…";
}

interface CassetteProps {
  cassetteStyle: string;
  title: string;
  tracks: Track[];
  side: "A" | "B";
}

const Cassette: React.FC<CassetteProps> = ({
  cassetteStyle,
  title,
  tracks,
  side,
}) => {
  const theme: CassetteTheme = CASSETTE_THEMES[cassetteStyle] ?? DEFAULT_THEME;

  const sideTracks = tracks.filter((t) => t.side === side);
  const visibleTracks = sideTracks.slice(0, MAX_VISIBLE_TRACKS);
  const hiddenCount = sideTracks.length - visibleTracks.length;

  const labelText = visibleTracks.map((t) => truncate(t.title)).join(" - ");

  return (
    <div style={{ ...cassetteStyles.shell, backgroundColor: theme.body }}>
      {/* Label */}
      <div style={{ ...cassetteStyles.label, backgroundColor: theme.label }}>
        <p style={{ ...cassetteStyles.labelText, color: theme.text }}>
          {labelText || "No tracks yet"}
          {hiddenCount > 0 && (
            <span style={{ opacity: 0.6 }}> + {hiddenCount} more</span>
          )}
        </p>
      </div>

      {/* Reels */}
      <div style={cassetteStyles.reelRow}>
        <div
          style={{
            ...cassetteStyles.reel,
            backgroundColor: theme.reel,
            borderColor: theme.accent,
          }}
        >
          <div
            style={{ ...cassetteStyles.reelHub, backgroundColor: theme.accent }}
          />
        </div>
        <div
          style={{
            ...cassetteStyles.reel,
            backgroundColor: theme.reel,
            borderColor: theme.accent,
          }}
        >
          <div
            style={{ ...cassetteStyles.reelHub, backgroundColor: theme.accent }}
          />
        </div>
      </div>

      {/* Footer */}
      <div style={{ ...cassetteStyles.footer, backgroundColor: theme.accent }}>
        <span style={{ ...cassetteStyles.footerText, color: theme.body }}>
          {title}
        </span>
      </div>
    </div>
  );
};

export { Cassette };

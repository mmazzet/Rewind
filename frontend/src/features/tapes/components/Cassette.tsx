import React from "react";
import { CASSETTE_THEMES, DEFAULT_THEME } from "./Cassette.styles";
import type { CassetteTheme } from "./Cassette.styles";
import type { Track } from "../types";

const MAX_VISIBLE_TRACKS = 7;
const MAX_TITLE_LENGTH = 20;

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

  // Build the label text: titles separated by dashes
  const labelText = visibleTracks.map((t) => truncate(t.title)).join(" - ");

  return (
    <div
      style={{
        width: "340px",
        height: "210px",
        backgroundColor: theme.body,
        borderRadius: "10px",
        boxShadow: "0 4px 16px rgba(0,0,0,0.4)",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
        boxSizing: "border-box",
      }}
    >
      {/* Label area */}
      <div
        style={{
          backgroundColor: theme.label,
          margin: "10px 10px 0 10px",
          borderRadius: "4px 4px 0 0",
          padding: "8px 10px",
          flex: "1",
          overflow: "hidden",
        }}
      >
        <p
          style={{
            fontFamily: "'Caveat', cursive",
            fontSize: "15px",
            color: theme.text,
            margin: 0,
            lineHeight: "1.5",
            wordBreak: "break-word",
          }}
        >
          {labelText || "No tracks yet"}
          {hiddenCount > 0 && (
            <span style={{ opacity: 0.6 }}> + {hiddenCount} more</span>
          )}
        </p>
      </div>

      {/* Reel row */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-around",
          alignItems: "center",
          width: "100%",
          marginTop: "16px",
        }}
      >
        {/* Left reel */}
        <div
          style={{
            width: "72px",
            height: "72px",
            borderRadius: "50%",
            backgroundColor: theme.reel,
            border: `3px solid ${theme.accent}`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <div
            style={{
              width: "24px",
              height: "24px",
              borderRadius: "50%",
              backgroundColor: theme.accent,
            }}
          />
        </div>

        {/* Right reel */}
        <div
          style={{
            width: "72px",
            height: "72px",
            borderRadius: "50%",
            backgroundColor: theme.reel,
            border: `3px solid ${theme.accent}`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <div
            style={{
              width: "24px",
              height: "24px",
              borderRadius: "50%",
              backgroundColor: theme.accent,
            }}
          />
        </div>
      </div>

      {/* Footer strip — tape title */}
      <div
        style={{
          backgroundColor: theme.accent,
          margin: "0 10px 10px 10px",
          borderRadius: "0 0 4px 4px",
          padding: "4px 10px",
        }}
      >
        <span
          style={{
            fontFamily: "'Special Elite', cursive",
            fontSize: "15px",
            color: theme.body,
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
            display: "block",
          }}
        >
          {title}
        </span>
      </div>
    </div>
  );
};

export { Cassette };

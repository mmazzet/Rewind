export interface CassetteTheme {
  body: string;
  label: string;
  accent: string;
  reel: string;
  text: string;
}

export const CASSETTE_THEMES: Record<string, CassetteTheme> = {
  classic: {
    body: "#1a1a1a",
    label: "#f5f0e8",
    accent: "#c0c0c0",
    reel: "#333333",
    text: "#1a1a1a",
  },
  chrome: {
    body: "#2a3f5f",
    label: "#dce8f5",
    accent: "#7eb8d4",
    reel: "#1a2d45",
    text: "#1a2d45",
  },
  metal: {
    body: "#2d2d2d",
    label: "#e8e0d0",
    accent: "#b8860b",
    reel: "#1a1a1a",
    text: "#2d2d2d",
  },
  vintage: {
    body: "#5c3d1e",
    label: "#f0e6c8",
    accent: "#8b6914",
    reel: "#3d2810",
    text: "#3d2810",
  },
};

export const DEFAULT_THEME = CASSETTE_THEMES.classic;

export const cassetteStyles = {
  shell: {
    width: "min(380px, 92vw)",
    height: "min(240px, 58vw)",
    maxWidth: "100%",
    boxSizing: "border-box" as const,
    borderRadius: "10px",
    boxShadow: "0 4px 16px rgba(0,0,0,0.4)",
    display: "flex",
    flexDirection: "column" as const,
    overflow: "hidden",
  },
  label: {
    margin: "10px 10px 0 10px",
    borderRadius: "4px 4px 0 0",
    padding: "8px 10px",
    flex: "1",
    overflow: "hidden",
  },
  labelText: {
    fontFamily: "'Caveat', cursive",
    fontSize: "15px",
    fontWeight: "bold",
    margin: 0,
    lineHeight: "1.5",
    wordBreak: "break-word" as const,
  },
  reelRow: {
    display: "flex",
    justifyContent: "space-around",
    alignItems: "center",
    width: "100%",
    marginTop: "28px",
    marginBottom: "16px",
  },
  reel: {
    width: "72px",
    height: "72px",
    borderRadius: "50%",
    border: "3px solid",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  reelHub: {
    width: "24px",
    height: "24px",
    borderRadius: "50%",
  },
  footer: {
    margin: "0 10px 10px 10px",
    borderRadius: "0 0 4px 4px",
    padding: "4px 10px",
  },
  footerText: {
    fontFamily: "'Special Elite', cursive",
    fontSize: "15px",
    fontWeight: "bold",
    whiteSpace: "nowrap" as const,
    overflow: "hidden",
    textOverflow: "ellipsis",
    display: "block",
  },
};

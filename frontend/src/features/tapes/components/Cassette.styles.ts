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

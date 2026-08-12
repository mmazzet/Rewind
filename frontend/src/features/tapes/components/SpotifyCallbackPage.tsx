import React, { useEffect, useRef } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { spotifyApi } from "../api/spotifyApi";

const SpotifyCallbackPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  // Prevent the effect running twice in React strict mode
  const called = useRef(false);

  useEffect(() => {
    if (called.current) return;
    called.current = true;

    const code = searchParams.get("code");
    const error = searchParams.get("error");

    if (error || !code) {
      navigate("/outbox?spotify=denied", { replace: true });
      return;
    }

    spotifyApi
      .connectSpotify(code)
      .then(() => {
        navigate("/outbox?spotify=connected", { replace: true });
      })
      .catch(() => {
        navigate("/outbox?spotify=denied", { replace: true });
      });
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <p className="text-gray-500">Connecting Spotify...</p>
    </div>
  );
};

export default SpotifyCallbackPage;

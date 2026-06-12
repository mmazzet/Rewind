from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_expiry_days: int = 7
    env: str = "development"

    spotify_client_id: str | None = None
    spotify_client_secret: str | None = None
    spotify_mock: bool = False

    model_config = {"env_file": ".env"}


def require_spotify_credentials() -> tuple[str, str]:
    """Raise a clear error if Spotify credentials are not configured."""
    if not settings.spotify_client_id or not settings.spotify_client_secret:
        raise ValueError(
            "Spotify credentials not configured. "
            "Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env"
        )
    return settings.spotify_client_id, settings.spotify_client_secret


settings = Settings()

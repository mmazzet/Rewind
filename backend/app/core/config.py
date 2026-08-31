from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    ssl_mode: str = "disable"
    jwt_secret: str
    jwt_expiry_days: int = 7
    env: str = "development"
    public_base_url: str
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    spotify_client_id: str | None = None
    spotify_client_secret: str | None = None
    spotify_mock: bool = False
    spotify_redirect_uri: str

    resend_api_key: str | None = None
    resend_from_email: str | None = None

    model_config = {"env_file": ".env", "extra": "ignore"}


def require_spotify_credentials() -> tuple[str, str]:
    """Raise a clear error if Spotify credentials are not configured."""
    if not settings.spotify_client_id or not settings.spotify_client_secret:
        raise ValueError(
            "Spotify credentials not configured. "
            "Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env"
        )
    return settings.spotify_client_id, settings.spotify_client_secret


def require_resend_credentials() -> str:
    """Raise a clear error if the Resend API key is not configured."""
    if not settings.resend_api_key:
        raise ValueError("Resend API key not configured. " "Set RESEND_API_KEY in .env")
    return settings.resend_api_key


def require_resend_from_email() -> str:
    """Raise a clear error if the Resend sender address is not configured."""
    if not settings.resend_from_email:
        raise ValueError(
            "Resend sender address not configured. " "Set RESEND_FROM_EMAIL in .env"
        )
    return settings.resend_from_email


settings = Settings()

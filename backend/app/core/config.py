from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_expiry_days: int = 7
    env: str = "development"

    spotify_client_id: str
    spotify_client_secret: str
    spotify_mock: bool = False

    model_config = {"env_file": ".env"}


settings = Settings()

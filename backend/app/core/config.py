from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    env: str = "development"

    model_config = {"env_file": ".env"}


settings = Settings()

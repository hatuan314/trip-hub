from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "itinerary-service"
    environment: str = "local"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg2://trip:trip@postgres:5432/trip_hub"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> "Settings":
    return Settings()


settings = get_settings()

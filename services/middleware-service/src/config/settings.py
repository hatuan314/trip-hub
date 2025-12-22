from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "middleware-service"
    environment: str = "local"
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"
    http_timeout: float = Field(default=10.0, gt=0)

    destination_service_url: str = "http://destination-service:8001"
    itinerary_service_url: str = "http://itinerary-service:8002"
    booking_service_url: str = "http://booking-service:8003"
    weather_service_url: str = "http://weather-service:8004"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> "Settings":
    return Settings()


settings = get_settings()

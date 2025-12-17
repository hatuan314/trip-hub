from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Booking Service"
    app_version: str = "1.0.0"
    debug: bool = True
    
    amadeus_api_key: str = "vufTw1626D0b6oBAOc4imErAWpvEGVFR"
    amadeus_api_secret: str = "dCILSPjIHv40Hyfg"
    amadeus_base_url: str = "https://test.api.amadeus.com"
    
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    cache_ttl: int = 3600
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()

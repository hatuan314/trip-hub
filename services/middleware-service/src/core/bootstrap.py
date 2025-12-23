from src.config.settings import settings
from src.core.service_router import ServiceRouter

# Central registry that maps incoming service keys to downstream base URLs.
service_router = ServiceRouter(
    {
        "destination": settings.destination_service_url,
        "weather": settings.weather_service_url,
    },
    api_prefix=settings.api_prefix,
)

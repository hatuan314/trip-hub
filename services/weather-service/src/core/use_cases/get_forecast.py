from src.core.entities.weather import Weather
from src.infrastructure.external.openweather_client import OpenWeatherClient


class GetForecast:
    """Use case: get forecast."""

    def __init__(self, client: OpenWeatherClient):
        self.client = client

    async def execute(self, location: str) -> list[Weather]:
        return await self.client.forecast(location)

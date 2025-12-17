from src.core.entities.weather import Weather
from src.infrastructure.external.openweather_client import OpenWeatherClient


class GetCurrentWeather:
    """Use case: get current weather."""

    def __init__(self, client: OpenWeatherClient):
        self.client = client

    async def execute(self, location: str) -> Weather:
        return await self.client.current_weather(location)

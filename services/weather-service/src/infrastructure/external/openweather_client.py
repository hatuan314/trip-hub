from __future__ import annotations

import httpx

from src.core.entities.weather import Weather


class OpenWeatherClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openweathermap.org/data/2.5",
        units: str = "metric",
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.units = units

    async def current_weather(self, location: str) -> Weather:
        url = f"{self.base_url}/weather"
        params = {"q": location, "appid": self.api_key, "units": self.units}
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        return Weather(
            location=data.get("name") or location,
            temperature=float(data["main"]["temp"]) if data.get("main") and "temp" in data["main"] else None,
            description=(data.get("weather") or [{}])[0].get("description"),
        )

    async def forecast(self, location: str) -> list[Weather]:
        url = f"{self.base_url}/forecast"
        params = {"q": location, "appid": self.api_key, "units": self.units}
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        items = data.get("list") or []
        forecasts: list[Weather] = []
        for item in items:
            forecasts.append(
                Weather(
                    location=data.get("city", {}).get("name") or location,
                    temperature=float(item["main"]["temp"]) if item.get("main") and "temp" in item["main"] else None,
                    description=(item.get("weather") or [{}])[0].get("description"),
                )
            )
        return forecasts

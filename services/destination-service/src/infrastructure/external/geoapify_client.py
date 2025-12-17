from __future__ import annotations

import httpx

from src.core.entities.attraction import Attraction
from src.core.entities.destination import Destination
from src.core.entities.hotel import Hotel
from src.core.interfaces.external_api_client import ExternalApiClient


class GeoapifyClient(ExternalApiClient):
    def __init__(
        self,
        api_key: str,
        geocode_url: str = "https://api.geoapify.com/v1/geocode/search",
        places_url: str = "https://api.geoapify.com/v2/places",
        language: str = "en",
    ) -> None:
        self.api_key = api_key
        self.geocode_url = geocode_url
        self.places_url = places_url
        self.language = language

    async def _get(self, url: str, params: dict) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    async def search(self, query: str) -> list[Destination]:
        params = {"text": query, "format": "json", "lang": self.language, "apiKey": self.api_key}
        payload = await self._get(self.geocode_url, params)

        results: list[Destination] = []
        for item in payload.get("results", []):
            results.append(
                Destination(
                    id=str(
                        item.get("place_id")
                        or item.get("osm_id")
                        or item.get("datasource", {}).get("raw", {}).get("place_id")
                        or item.get("formatted")
                        or query
                    ),
                    name=item.get("name") or item.get("formatted") or query,
                    country=item.get("country"),
                    description=item.get("formatted"),
                )
            )
        return results

    async def geocode(self, query: str) -> tuple[float, float] | None:
        params = {"text": query, "format": "json", "lang": self.language, "apiKey": self.api_key}
        payload = await self._get(self.geocode_url, params)
        first = (payload.get("results") or [None])[0]
        if not first:
            return None
        return float(first["lon"]), float(first["lat"])

    async def _places(
        self,
        categories: str,
        lon: float,
        lat: float,
        radius_m: int = 5000,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict]:
        params = {
            "categories": categories,
            "filter": f"circle:{lon},{lat},{radius_m}",
            "bias": f"proximity:{lon},{lat}",
            "limit": limit,
            "offset": offset,
            "lang": self.language,
            "apiKey": self.api_key,
        }
        payload = await self._get(self.places_url, params)
        return payload.get("features", [])

    async def attractions_near(
        self,
        lon: float,
        lat: float,
        destination_ref: str,
        radius_m: int = 5000,
        limit: int = 20,
    ) -> list[Attraction]:
        features = await self._places("tourism", lon, lat, radius_m=radius_m, limit=limit)
        attractions: list[Attraction] = []
        for feature in features:
            props = feature.get("properties", {})
            attractions.append(
                Attraction(
                    id=str(props.get("place_id") or props.get("datasource", {}).get("raw", {}).get("place_id") or props.get("name") or props.get("formatted")),
                    destination_id=destination_ref,
                    name=props.get("name") or props.get("formatted") or "Attraction",
                )
            )
        return attractions

    async def hotels_near(
        self,
        lon: float,
        lat: float,
        destination_ref: str,
        radius_m: int = 5000,
        limit: int = 20,
    ) -> list[Hotel]:
        features = await self._places("accommodation.hotel", lon, lat, radius_m=radius_m, limit=limit)
        hotels: list[Hotel] = []
        for feature in features:
            props = feature.get("properties", {})
            hotels.append(
                Hotel(
                    id=str(props.get("place_id") or props.get("datasource", {}).get("raw", {}).get("place_id") or props.get("name") or props.get("formatted")),
                    destination_id=destination_ref,
                    name=props.get("name") or props.get("formatted") or "Hotel",
                )
            )
        return hotels

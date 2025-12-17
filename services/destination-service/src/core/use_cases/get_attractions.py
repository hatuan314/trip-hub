from src.core.entities.attraction import Attraction
from src.infrastructure.external.geoapify_client import GeoapifyClient


class GetAttractions:
    """Use case: list attractions near a destination."""

    def __init__(self, client: GeoapifyClient):
        self.client = client

    async def execute(self, location: str, radius_m: int = 5000, limit: int = 20) -> list[Attraction]:
        coords = await self.client.geocode(location)
        if not coords:
            return []
        lon, lat = coords
        return await self.client.attractions_near(lon=lon, lat=lat, destination_ref=location, radius_m=radius_m, limit=limit)

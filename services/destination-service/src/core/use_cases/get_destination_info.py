from src.core.entities.destination import Destination
from src.infrastructure.external.geoapify_client import GeoapifyClient


class GetDestinationInfo:
    """Use case: fetch destination detail via Geoapify search."""

    def __init__(self, client: GeoapifyClient):
        self.client = client

    async def execute(self, destination_query: str) -> Destination | None:
        results = await self.client.search(destination_query)
        return results[0] if results else None

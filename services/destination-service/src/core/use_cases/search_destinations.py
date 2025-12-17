import asyncio
from typing import Iterable

from src.core.entities.destination import Destination
from src.core.interfaces.external_api_client import ExternalApiClient


class SearchDestinations:
    """Use case: search destinations by keyword."""

    def __init__(self, clients: Iterable[ExternalApiClient]):
        self.clients = list(clients)

    async def execute(self, query: str, country: str | None = None) -> list[Destination]:
        tasks = [client.search(query) for client in self.clients]
        if not tasks:
            return []

        results: list[Destination] = []
        for result in await asyncio.gather(*tasks, return_exceptions=True):
            if isinstance(result, Exception):
                continue
            results.extend(result)

        if country:
            country_lower = country.lower()
            results = [dest for dest in results if (dest.country or "").lower() == country_lower]

        deduped: list[Destination] = []
        seen_ids: set[str] = set()
        for dest in results:
            if dest.id in seen_ids:
                continue
            seen_ids.add(dest.id)
            deduped.append(dest)

        return deduped

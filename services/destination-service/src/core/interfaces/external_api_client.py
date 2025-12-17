from abc import ABC, abstractmethod
from src.core.entities.destination import Destination


class ExternalApiClient(ABC):
    @abstractmethod
    async def search(self, query: str) -> list[Destination]:
        raise NotImplementedError

from abc import ABC, abstractmethod
from typing import Iterable
from src.core.entities.destination import Destination
from src.core.entities.attraction import Attraction
from src.core.entities.hotel import Hotel


class DestinationRepository(ABC):
    @abstractmethod
    def list_destinations(self) -> Iterable[Destination]:
        raise NotImplementedError


    @abstractmethod
    def get(self, destination_id: str) -> Destination | None:
        raise NotImplementedError


    @abstractmethod
    def list_attractions(self, destination_id: str) -> Iterable[Attraction]:
        raise NotImplementedError


    @abstractmethod
    def list_hotels(self, destination_id: str) -> Iterable[Hotel]:
        raise NotImplementedError

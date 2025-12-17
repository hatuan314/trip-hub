from dataclasses import dataclass


@dataclass
class Attraction:
    id: str
    destination_id: str
    name: str

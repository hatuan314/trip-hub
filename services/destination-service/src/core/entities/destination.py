from dataclasses import dataclass


@dataclass
class Destination:
    id: str
    name: str
    country: str | None = None
    description: str | None = None

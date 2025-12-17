from dataclasses import dataclass

@dataclass
class Weather:
    location: str
    temperature: float | None = None
    description: str | None = None

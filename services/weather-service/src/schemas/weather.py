from pydantic import BaseModel

class WeatherOut(BaseModel):
    location: str
    temperature: float | None = None
    description: str | None = None

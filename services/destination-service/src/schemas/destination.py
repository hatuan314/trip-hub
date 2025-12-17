from pydantic import BaseModel


class DestinationOut(BaseModel):
    id: str
    name: str
    country: str | None = None
    description: str | None = None

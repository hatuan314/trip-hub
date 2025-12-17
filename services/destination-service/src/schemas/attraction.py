from pydantic import BaseModel


class AttractionOut(BaseModel):
    id: str
    destination_id: str
    name: str

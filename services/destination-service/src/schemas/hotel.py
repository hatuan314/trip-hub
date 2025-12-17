from pydantic import BaseModel


class HotelOut(BaseModel):
    id: str
    destination_id: str
    name: str

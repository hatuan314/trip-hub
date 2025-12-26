from pydantic import BaseModel
from datetime import datetime


class ActivityCreate(BaseModel):
    itinerary_id: str
    title: str
    start_time: datetime
    end_time: datetime
    location: str
    note: str | None = None

from pydantic import BaseModel
from datetime import datetime

class ActivityCreate(BaseModel):
    itinerary_id: int
    name: str
    start_time: datetime
    end_time: datetime
    location: str
from pydantic import BaseModel
from datetime import date
from typing import Optional

class ItineraryCreate(BaseModel):
    title: str
    start_date: date
    end_date: date
    description: Optional[str] = None
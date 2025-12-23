from fastapi import APIRouter
from src.schemas.itinerary import ItineraryCreate

router = APIRouter()


@router.post("/")
def create_itinerary(data: ItineraryCreate):
    return {"message": "created", "data": data}

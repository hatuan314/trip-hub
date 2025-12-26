from fastapi import APIRouter, Depends
from src.schemas.itinerary import ItineraryCreate
from src.api.v1.dependencies import get_current_user
from src.infrastructure.itinerary_repo import ItineraryRepo

router = APIRouter()
repo = ItineraryRepo()


@router.post("/")
def create_itinerary(payload: ItineraryCreate, user=Depends(get_current_user)):
    return repo.create(user["username"], payload)


@router.get("/")
def list_itineraries(user=Depends(get_current_user)):
    return repo.list_by_user(user["username"])

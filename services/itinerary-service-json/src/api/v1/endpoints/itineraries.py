from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.schemas.itinerary import ItineraryCreate
from src.api.v1.dependencies import get_current_user, get_db
from src.infrastructure.itinerary_repo import ItineraryRepo

router = APIRouter()


@router.post("/")
def create_itinerary(
    payload: ItineraryCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = ItineraryRepo(db)
    return repo.create(user["username"], payload)


@router.get("/")
def list_itineraries(user=Depends(get_current_user), db: Session = Depends(get_db)):
    repo = ItineraryRepo(db)
    return repo.list_by_user(user["username"])

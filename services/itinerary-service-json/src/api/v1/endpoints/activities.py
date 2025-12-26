from fastapi import APIRouter, Depends
from src.schemas.activity import ActivityCreate
from src.api.v1.dependencies import get_current_user
from src.infrastructure.activity_repo import ActivityRepo

router = APIRouter()
repo = ActivityRepo()


@router.post("/")
def create_activity(payload: ActivityCreate, user=Depends(get_current_user)):
    return repo.create(user, payload)


@router.get("/{itinerary_id}")
def list_activities(itinerary_id: str, user=Depends(get_current_user)):
    return repo.list_by_itinerary(user, itinerary_id)

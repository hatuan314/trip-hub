from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.schemas.activity import ActivityCreate
from src.api.v1.dependencies import get_current_user, get_db
from src.infrastructure.activity_repo import ActivityRepo

router = APIRouter()


@router.post("/")
def create_activity(
    payload: ActivityCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = ActivityRepo(db)
    return repo.create(user["username"], payload)


@router.get("/{itinerary_id}")
def list_activities(
    itinerary_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)
):
    repo = ActivityRepo(db)
    return repo.list_by_itinerary(user["username"], itinerary_id)

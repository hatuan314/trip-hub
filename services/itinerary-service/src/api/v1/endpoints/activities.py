from fastapi import APIRouter
from src.schemas.activity import ActivityCreate

router = APIRouter()


@router.post("/")
def add_activity(data: ActivityCreate):
    return {"message": "activity added", "data": data}

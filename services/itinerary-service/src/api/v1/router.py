from fastapi import APIRouter
from src.api.v1.endpoints import itineraries, activities

router = APIRouter()
router.include_router(itineraries.router, prefix="/itineraries", tags=["Itineraries"])
router.include_router(activities.router, prefix="/activities", tags=["Activities"])

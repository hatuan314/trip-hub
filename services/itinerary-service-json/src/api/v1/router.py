from fastapi import APIRouter
from src.api.v1.endpoints import auth, itineraries, activities

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(itineraries.router, prefix="/itineraries", tags=["Itineraries"])
router.include_router(activities.router, prefix="/activities", tags=["Activities"])

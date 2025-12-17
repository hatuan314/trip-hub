from fastapi import APIRouter
from .endpoints import attractions, destinations, hotels, search


api_router = APIRouter()
api_router.include_router(destinations.router, prefix="/destinations", tags=["destinations"])
api_router.include_router(attractions.router, prefix="/attractions", tags=["attractions"])
api_router.include_router(hotels.router, prefix="/hotels", tags=["hotels"])
api_router.include_router(search.router, prefix="/search", tags=["search"])

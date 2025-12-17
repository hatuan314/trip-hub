from fastapi import APIRouter
from api.v1.endpoints import flights, hotels, cities

api_router = APIRouter()

api_router.include_router(flights.router)
api_router.include_router(hotels.router)
api_router.include_router(cities.router)

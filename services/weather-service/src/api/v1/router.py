from fastapi import APIRouter
from .endpoints import weather, forecast

api_router = APIRouter()
api_router.include_router(weather.router, prefix="/weather", tags=["weather"])
api_router.include_router(forecast.router, prefix="/forecast", tags=["forecast"])

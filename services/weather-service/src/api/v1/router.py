from fastapi import APIRouter
from .endpoints import weather, forecast

api_router = APIRouter()
# Nhóm endpoint thời tiết hiện tại và dự báo.
api_router.include_router(weather.router, prefix="/weather", tags=["weather"])
api_router.include_router(forecast.router, prefix="/forecast", tags=["forecast"])

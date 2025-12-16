from fastapi import APIRouter
from api.v1.endpoints import flights

api_router = APIRouter()

api_router.include_router(flights.router)

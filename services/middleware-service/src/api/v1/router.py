from fastapi import APIRouter
from src.api.v1.endpoints import auth
from .endpoints import proxy

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(proxy.router, tags=["proxy"])

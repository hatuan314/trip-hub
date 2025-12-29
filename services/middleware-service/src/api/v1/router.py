from fastapi import APIRouter
from src.api.v1.endpoints import auth
from .endpoints import proxy, wrappers

api_router = APIRouter()
# Auth + proxy endpoints cho middleware.
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(wrappers.router, tags=["proxy wrappers"])
api_router.include_router(proxy.router, tags=["proxy"])

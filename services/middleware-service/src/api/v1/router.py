from fastapi import APIRouter

from .endpoints import proxy, services

api_router = APIRouter()
# IMPORTANT: Include services router BEFORE proxy to avoid wildcard conflicts
api_router.include_router(services.router, tags=["info"])
api_router.include_router(proxy.router, tags=["proxy"])

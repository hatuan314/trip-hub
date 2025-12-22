from fastapi import APIRouter

from .endpoints import proxy

api_router = APIRouter()
api_router.include_router(proxy.router, tags=["proxy"])

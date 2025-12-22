from fastapi import FastAPI

from src.api.v1.router import api_router
from src.config.settings import settings
from src.core.bootstrap import service_router


app = FastAPI(title="Middleware Service", version="0.1.0")


@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
        "forwarding_to": service_router.available_services(),
    }


app.include_router(api_router, prefix=settings.api_prefix)

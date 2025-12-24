from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.api.v1.router import api_router
from src.config.settings import settings
from src.core.bootstrap import service_router

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Middleware Service (API Gateway)",
    version="0.1.0",
    description="API Gateway - Điểm vào trung tâm cho tất cả microservices trong hệ thống Trip Hub",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_prefix)


@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.app_name}")
    logger.info(f"Available services: {', '.join(service_router.available_services())}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {settings.app_name}")


@app.get("/", tags=["info"])
async def root():
    return {
        "service": settings.app_name,
        "version": "0.1.0",
        "status": "running",
        "role": "API Gateway",
        "docs": "/api/docs",
        "available_services": service_router.available_services(),
        "routing_pattern": "/api/v1/{service}/{path}",
        "quick_examples": {
            "destination": "/api/v1/destination/destinations",
            "weather": "/api/v1/weather/forecast?city=hanoi",
            "booking": "/api/v1/booking/flights/search",
            "itinerary": "/api/v1/itinerary/itineraries"
        },
        "detailed_api_docs": {
            "all_services": "/api/v1/services",
            "specific_service": "/api/v1/services/{service_name}",
            "swagger_ui": "/api/docs"
        }
    }


@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
        "forwarding_to": service_router.available_services(),
    }

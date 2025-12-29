from fastapi import FastAPI
from src.api.v1.router import api_router

app = FastAPI(title="Weather Service", version="0.1.0")

@app.get("/health", tags=["health"])
async def health_check():
    # Health check đơn giản cho weather-service.
    return {"status": "ok"}

# Gắn router chính cho các endpoint /api/v1/...
app.include_router(api_router, prefix="/api/v1")

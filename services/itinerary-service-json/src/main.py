from fastapi import FastAPI
from src.api.v1.router import router
from src.infrastructure.database.connection import init_db

app = FastAPI(title="Itinerary Service")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "service": "itinerary-service-json"}


app.include_router(router, prefix="/api/v1")

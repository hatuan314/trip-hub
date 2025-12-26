from fastapi import FastAPI
from src.api.v1.router import router

app = FastAPI(title="Itinerary Service")
app.include_router(router, prefix="/api/v1")

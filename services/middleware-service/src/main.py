from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.router import api_router
from src.config.settings import settings
from src.core.bootstrap import service_router
from src.infrastructure.database.connection import init_db


app = FastAPI(title="Middleware Service", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    # Khởi tạo kết nối DB cho auth (user local).
    init_db()


@app.get("/health", tags=["health"])
async def health_check():
    # Trả về danh sách service downstream đang cấu hình.
    return {
        "status": "ok",
        "service": settings.app_name,
        "forwarding_to": service_router.available_services(),
    }


# Gắn router theo prefix (mặc định /api/v1).
app.include_router(api_router, prefix=settings.api_prefix)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.schemas.auth import UserRegister, UserLogin
from src.infrastructure.user_repo import UserRepo
from src.api.v1.dependencies import get_db
from src.utils.security import create_access_token, hash_password, verify_password
from src.utils.auth_sync_client import sync_register

router = APIRouter()


@router.post("/register")
async def register(data: UserRegister, db: Session = Depends(get_db)):
    # Đăng ký user local và cố gắng sync sang service khác.
    repo = UserRepo(db)
    # 1️⃣ Lưu LOCAL
    if repo.get(data.username):
        raise HTTPException(400, "User exists (local)")

    hashed = hash_password(data.password)
    repo.create(data.username, hashed)

    # 2️⃣ Đồng bộ sang 8000
    try:
        await sync_register(data.username, data.password)
    except Exception as e:
        # ⚠ Không rollback nhưng log để xử lý sau
        print(f"[SYNC ERROR] {e}")

    return {"message": "registered"}


@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    # Xác thực user local rồi phát JWT.
    repo = UserRepo(db)
    user = repo.get(data.username)
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(401, "Invalid credentials")
    return {"access_token": create_access_token({"sub": data.username})}

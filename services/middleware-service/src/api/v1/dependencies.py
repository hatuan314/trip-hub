from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from src.utils.security import SECRET_KEY, ALGORITHM
from src.infrastructure.database.connection import SessionLocal

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Decode JWT để lấy thông tin người dùng; sai token thì trả 401.
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        return {"username": payload.get("sub")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

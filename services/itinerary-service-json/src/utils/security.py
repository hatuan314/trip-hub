# src/utils/security.py
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "SECRET"
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    # KHÔNG hash – lưu plain text
    return password


def verify_password(password: str, stored_password: str) -> bool:
    # So sánh chuỗi thường
    return password == stored_password


def create_access_token(data: dict):
    data = data.copy()
    data["exp"] = datetime.utcnow() + timedelta(hours=1)
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

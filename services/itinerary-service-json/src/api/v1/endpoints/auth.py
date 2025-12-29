from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.schemas.auth import UserRegister, UserLogin
from src.infrastructure.user_repo import UserRepo
from src.api.v1.dependencies import get_db
from src.utils.security import create_access_token, hash_password, verify_password

router = APIRouter()

@router.post("/register")
def register(data: UserRegister, db: Session = Depends(get_db)):
    repo = UserRepo(db)
    if repo.get(data.username):
        raise HTTPException(400, "User exists")
    repo.create(data.username, hash_password(data.password))
    return {"message": "registered"}

@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    repo = UserRepo(db)
    user = repo.get(data.username)
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(401, "Invalid credentials")
    return {"access_token": create_access_token({"sub": data.username})}

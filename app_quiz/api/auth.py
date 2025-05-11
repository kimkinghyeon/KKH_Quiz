from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import jwt
from passlib.context import CryptContext
from app_quiz.schemas import Token, UserCreate, TokenData
from app_quiz.models import User
from app_quiz.dependencies import get_db
from app_quiz.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(tags=["auth"])

@router.post("/auth/signup", response_model=Token)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    hashed = pwd_context.hash(user_in.password)
    user = User(email=user_in.email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    access_token = jwt.encode({"sub": str(user.id)}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect credentials")
    access_token = jwt.encode(
        {"sub": str(user.id)}, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return {"access_token": access_token, "token_type": "bearer"}
from typing import List
from fastapi import APIRouter, HTTPException, Path, status
from fastapi import Depends
import fastapi
from config import SessionLocal
from sqlalchemy.orm import Session
from schemas import UserSchema
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from jwt import create_access_token
from models import User


router = APIRouter()

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router.post('/token')
async def login (request: UserSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email & User.password==request.password).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")
    access_token = create_access_token(data={"sub": user.email, "id": user.id, "name": user.name, "lastname": user.lastname})
    return {"access_token": access_token, "token_type": "bearer"}
    
@router.post('/token/form')
async def login (request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")
    access_token = create_access_token(data={"sub": user.email, "id": user.id, "name": user.name, "lastname": user.lastname})
    return {"access_token": access_token, "token_type": "bearer"}
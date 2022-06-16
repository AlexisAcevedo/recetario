from typing import List
from fastapi import APIRouter, HTTPException, Path, status
from fastapi import Depends
import fastapi
from config import SessionLocal
from sqlalchemy.orm import Session
from schemas import UserSchema
import userService
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import get_current_user
from utils import validate_email

router = APIRouter()

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

#GET USERS
@router.get("")
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user))  -> List[UserSchema]: 
    try:
        _users = userService.get_user(db, skip, limit)
        return list(_users) 
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str("No hay usuarios"))

#GET USER by ID
@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(user_id: int, db: Session = Depends(get_db))  -> UserSchema:
    try:
        _user = userService.get_user_by_id(db, user_id)
        return _user.name
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str("Usuario inexistente"))

#CREATE USER
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(request: UserSchema, db: Session = Depends(get_db)):
        validate_email(email=request.email)
        return userService.create_user(db=db, user=request)
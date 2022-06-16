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

#GET USER             
@router.get("", status_code=status.HTTP_200_OK)
async def get_user(db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user))  -> UserSchema:
    return current_user

#PATCH USER
#FALTA CORREGIR STATUS CODE
@router.patch("", status_code=status.HTTP_200_OK)
async def update_user(request: UserSchema, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):  
    try:
        user = userService.update_user(db=db, user_id=current_user.id, email=request.email, password=request.password, name=request.name, lastname=request.lastname)
        return user
    except Exception as e:  
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str("Bad Request"))
    
#DELETE USER
@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(request: UserSchema, db: Session = Depends(get_db),  current_user: UserSchema = Depends(get_current_user)):
    try:
        user = userService.delete_user(db=db, user_id=request.id)
        return  f"User {request.id} deleted"
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str("Usuario inexistente"))
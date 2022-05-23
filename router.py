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

router = APIRouter()

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
#CREATE USER
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(request: UserSchema, db: Session = Depends(get_db)):
    try: 
        user = userService.create_user(db=db, user=request)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str("Bad Request"))
    
#GET USERS
@router.get("")
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user))  -> List[UserSchema]: 
    try:
        _users = userService.get_user(db, skip, limit)
        return list(_users) 
    except Exception as e:
        raise HTTPException(status_code=400, detail=str("Bad Request"))

#PATCH USER
@router.patch("")
async def update_user(request: UserSchema, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):  
    try:
        user = userService.update_user(db=db, user_id=current_user.id, email=request.email, password=request.password, name=request.name, lastname=request.lastname)
        return user
    except Exception as e:  
        raise HTTPException(status_code=400, detail=str("Bad Request"))
    
#DELETE USER
@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(request: UserSchema, db: Session = Depends(get_db),  current_user: UserSchema = Depends(get_current_user)):
    try:
        user = userService.delete_user(db=db, user_id=request.id)
        return  f"User {request.id} deleted"
    except Exception as e:
        raise HTTPException(status_code=400, detail=str("Bad Request"))



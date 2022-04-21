from typing import List
from fastapi import APIRouter, HTTPException, Path
from fastapi import Depends
import fastapi
from config import SessionLocal
from sqlalchemy.orm import Session
from schemas import UserSchema
import userService

router = APIRouter()

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router.post("")
async def create_user(request: UserSchema, db: Session = Depends(get_db)):
    try: 
        user = userService.create_user(db=db, user=request)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str("Bad Request"))
    

@router.get("")
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db))  -> List[UserSchema]: 
    try:
        _users = userService.get_user(db, skip, limit)
        return list(_users) 
    except Exception as e:
        raise HTTPException(status_code=400, detail=str("Bad Request"))


@router.patch("")
async def update_user(request: UserSchema, db: Session = Depends(get_db)):  
    try:
        user = userService.update_user(db=db, user_id=request.id, username=request.username, password=request.password)
        return user
    except Exception as e:  
        raise HTTPException(status_code=400, detail=str("Bad Request"))
    


@router.delete("")
async def delete_user(request: UserSchema, db: Session = Depends(get_db)):
    try:
        user = userService.delete_user(db=db, user_id=request.id)
        return  f"User {request.id} deleted"
    except Exception as e:
        raise HTTPException(status_code=400, detail=str("Bad Request"))

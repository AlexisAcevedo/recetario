
from lib2to3.pgen2.token import OP
from typing import List, Optional, Generic, TypeVar
from unicodedata import name
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

T = TypeVar('T')

class UserSchema(BaseModel):
    id: Optional[int] = None
    email: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None
    lastname: Optional[str] = None

    class Config:
        orm_mode = True


class Login(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    id: Optional[int] = None
from lib2to3.pgen2.token import OP
from typing import List, Optional, Generic, TypeVar
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

T = TypeVar('T')

class UserSchema(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None

    class Config:
        orm_mode = True


#cambiar por "error" 
class Response(GenericModel, Generic[T]):
    #code: str
    #status: str
    message: str
    

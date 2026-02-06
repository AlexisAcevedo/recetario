"""
Esquemas Pydantic de Token.
Define los modelos para autenticación JWT.
"""
from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """
    Esquema para respuesta de token.
    
    Atributos:
        access_token: Token JWT codificado
        token_type: Tipo de token (siempre "bearer")
    """
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Esquema para datos decodificados del token.
    
    Contiene la información extraída del payload JWT.
    """
    email: Optional[str] = None
    user_id: Optional[int] = None
    name: Optional[str] = None
    lastname: Optional[str] = None

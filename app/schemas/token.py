"""
Token Pydantic schemas for authentication.
"""
from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """Schema for token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded token data."""
    email: Optional[str] = None
    user_id: Optional[int] = None
    name: Optional[str] = None
    lastname: Optional[str] = None

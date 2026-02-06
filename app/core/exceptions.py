"""
Custom exceptions for the application.
"""
from fastapi import HTTPException, status


class UserNotFoundException(HTTPException):
    """Raised when a user is not found."""
    def __init__(self, detail: str = "Usuario no encontrado"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class UserAlreadyExistsException(HTTPException):
    """Raised when trying to create a user that already exists."""
    def __init__(self, detail: str = "El email ya está registrado"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class InvalidCredentialsException(HTTPException):
    """Raised when login credentials are invalid."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"}
        )


class NotAuthenticatedException(HTTPException):
    """Raised when authentication is required but not provided."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
            headers={"WWW-Authenticate": "Bearer"}
        )

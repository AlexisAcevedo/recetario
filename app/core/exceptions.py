"""
Excepciones personalizadas de la aplicación.
Define excepciones HTTP específicas para manejo de errores consistente.
"""
from fastapi import HTTPException, status


class UserNotFoundException(HTTPException):
    """
    Excepción lanzada cuando no se encuentra un usuario.
    
    Código HTTP: 404 Not Found
    """
    
    def __init__(self, detail: str = "Usuario no encontrado"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class UserAlreadyExistsException(HTTPException):
    """
    Excepción lanzada cuando se intenta crear un usuario
    con un email que ya existe.
    
    Código HTTP: 400 Bad Request
    """
    
    def __init__(self, detail: str = "El email ya está registrado"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class InvalidCredentialsException(HTTPException):
    """
    Excepción lanzada cuando las credenciales de login son inválidas.
    
    Código HTTP: 401 Unauthorized
    Incluye header WWW-Authenticate para clientes OAuth2.
    """
    
    def __init__(self, detail: str = "Email o contraseña incorrectos"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class NotAuthenticatedException(HTTPException):
    """
    Excepción lanzada cuando se requiere autenticación
    pero no se proporcionó un token válido.
    
    Código HTTP: 401 Unauthorized
    """
    
    def __init__(self, detail: str = "No autenticado"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

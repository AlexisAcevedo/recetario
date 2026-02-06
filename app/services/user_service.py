"""
Servicio de Usuario - Lógica de negocio para operaciones de usuarios.
Contiene todas las operaciones CRUD y autenticación.
"""
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import UserNotFoundException, UserAlreadyExistsException


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Obtiene un usuario por su ID.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario a buscar
        
    Returns:
        Usuario encontrado o None si no existe
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Obtiene un usuario por su email.
    
    Args:
        db: Sesión de base de datos
        email: Email del usuario a buscar
        
    Returns:
        Usuario encontrado o None si no existe
    """
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Obtiene una lista de usuarios con paginación.
    
    Args:
        db: Sesión de base de datos
        skip: Número de registros a omitir
        limit: Máximo de registros a retornar
        
    Returns:
        Lista de usuarios
    """
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Crea un nuevo usuario.
    
    Args:
        db: Sesión de base de datos
        user_data: Datos del usuario a crear
        
    Returns:
        Usuario creado
        
    Raises:
        UserAlreadyExistsException: Si el email ya está registrado
    """
    # Verificar si el email ya existe
    if get_user_by_email(db, user_data.email):
        raise UserAlreadyExistsException()
    
    # Crear usuario con contraseña hasheada
    user = User(
        email=user_data.email,
        password=get_password_hash(user_data.password),
        name=user_data.name,
        lastname=user_data.lastname
    )
    
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        raise UserAlreadyExistsException()


def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
    """
    Actualiza un usuario existente.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario a actualizar
        user_data: Datos nuevos (solo campos proporcionados)
        
    Returns:
        Usuario actualizado
        
    Raises:
        UserNotFoundException: Si el usuario no existe
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise UserNotFoundException()
    
    # Actualizar solo campos proporcionados
    update_data = user_data.model_dump(exclude_unset=True)
    
    # Hashear contraseña si se está actualizando
    if "password" in update_data:
        update_data["password"] = get_password_hash(update_data["password"])
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    """
    Elimina un usuario.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario a eliminar
        
    Returns:
        True si se eliminó correctamente
        
    Raises:
        UserNotFoundException: Si el usuario no existe
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise UserNotFoundException()
    
    db.delete(user)
    db.commit()
    return True


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Autentica un usuario por email y contraseña.
    
    Args:
        db: Sesión de base de datos
        email: Email del usuario
        password: Contraseña en texto plano
        
    Returns:
        Usuario si las credenciales son válidas, None en caso contrario
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

"""
Configuración de la base de datos.
Maneja la conexión a PostgreSQL usando SQLAlchemy.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Crear motor de base de datos con pool de conexiones
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Verifica conexión antes de usar
    pool_size=5,         # Conexiones en el pool
    max_overflow=10      # Conexiones adicionales permitidas
)

# Fábrica de sesiones de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para modelos SQLAlchemy
Base = declarative_base()


def get_db():
    """
    Generador de sesiones de base de datos.
    
    Uso como dependencia de FastAPI para inyectar sesión en endpoints.
    La sesión se cierra automáticamente al finalizar la request.
    
    Yields:
        Session: Sesión de SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""
Configuración de la base de datos asíncrona.
Maneja la conexión a PostgreSQL usando SQLAlchemy 2.0 (Asyncio).
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# Asegurar que la URL use el esquema asíncrono
db_url = settings.database_url
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Crear motor asíncrono
engine = create_async_engine(
    db_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False  # Cambiar a True para debug de SQL
)

# Fábrica de sesiones asíncronas
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# Clase base para modelos (Uso de SQLAlchemy 2.0 compatible)
Base = declarative_base()


async def get_db():
    """
    Generador de sesiones asíncronas.
    """
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()


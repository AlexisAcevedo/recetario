"""
Recetario API - Punto de Entrada Principal

Aplicación FastAPI moderna para gestión de usuarios con autenticación JWT.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.router import router as api_v1_router

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.router import router as api_v1_router
from app.core.limiter import limiter

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Configuración de Rate Limiting trasladada a app.core.limiter para evitar ciclos




@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ciclo de vida de la aplicación.
    
    Se ejecuta al inicio y al cierre del servidor.
    """
    # Inicio: Crear tablas en la base de datos
    Base.metadata.create_all(bind=engine)
    yield
    # Cierre: Limpieza si es necesaria
    pass


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    description="API de gestión de usuarios para el sistema de recetario",
    version="2.0.0",
    lifespan=lifespan
)

# Conectar limiter a la app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configuración de CORS
origins = [
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers de la API
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/", tags=["health"])
async def root():
    """Endpoint de verificación de estado."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": "2.0.0"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Verificación de estado detallada."""
    return {
        "status": "healthy",
        "database": "connected"
    }

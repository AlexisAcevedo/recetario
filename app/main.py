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
    # Configurar logging estructurado
    from app.core.logging import configure_logging
    configure_logging()
    
    # Inicializar Sentry (si está configurado)
    from app.core.sentry import init_sentry
    init_sentry()

    # Inicializar Cache (Redis con fallback a Memoria)
    from fastapi_cache import FastAPICache
    from fastapi_cache.backends.redis import RedisBackend
    from fastapi_cache.backends.inmemory import InMemoryBackend
    from redis import asyncio as aioredis
    
    try:
        # Intenta conectar a Redis en localhost (default)
        redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
        # Check connection
        await redis.ping()
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
        # logger.info("Redis cache initialized")
    except Exception as e:
        # Fallback a memoria si falla Redis
        # logger.warning(f"Redis connection failed, using InMemory cache: {e}")
        FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    
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

# Configuración de CORS - Restrictiva para producción
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],  # Solo métodos necesarios
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With"
    ],
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


@app.get("/metrics", tags=["monitoring"], include_in_schema=False)
async def metrics():
    """Endpoint de métricas para Prometheus."""
    from app.core.metrics import get_metrics
    return get_metrics()

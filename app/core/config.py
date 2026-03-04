"""
Configuración de la aplicación.
Carga variables de entorno usando pydantic-settings.
"""
from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuración de la aplicación cargada desde variables de entorno.
    
    Atributos:
        app_name: Nombre de la aplicación
        debug: Modo debug activado/desactivado
        database_url: URL de conexión a PostgreSQL
        secret_key: Clave secreta para JWT
        algorithm: Algoritmo de encriptación JWT
        access_token_expire_minutes: Minutos de validez del access token
        refresh_token_expire_days: Días de validez del refresh token
    """
    
    # Configuración general
    app_name: str = "Recetario API"
    debug: bool = False
    
    # Base de datos
    database_url: str
    
    # Seguridad JWT
    secret_key: str
    
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("OWASP A04: La SECRET_KEY debe tener al menos 32 caracteres para asegurar una entropía adecuada.")
        return v
    
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15  # Reducido para mayor seguridad
    refresh_token_expire_days: int = 7     # Refresh token dura más
    
    # CORS
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8080",
        description="Orígenes CORS permitidos, separados por coma"
    )
    
    # Observabilidad
    sentry_dsn: str | None = Field(default=None, description="Sentry DSN para error tracking")
    environment: str = Field(default="development", description="Entorno de ejecución")
    
    def get_cors_origins_list(self) -> list[str]:
        """Convierte cors_origins string a lista."""
        origins = [origin.strip() for origin in self.cors_origins.split(",")]
        if self.environment.lower() == "production" and "*" in origins:
            raise ValueError("OWASP A01: CORS wildcard '*' is strictly forbidden in production")
        return origins
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene la instancia de configuración (cacheada).
    
    Returns:
        Instancia de Settings con la configuración cargada
    """
    return Settings()


# Instancia global de configuración
settings = get_settings()

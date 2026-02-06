"""
Configuración de la aplicación.
Carga variables de entorno usando pydantic-settings.
"""
from functools import lru_cache
from typing import Optional

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
        access_token_expire_minutes: Minutos de validez del token
    """
    
    # Configuración general
    app_name: str = "Recetario API"
    debug: bool = False
    
    # Base de datos
    database_url: str
    
    # Seguridad JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
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

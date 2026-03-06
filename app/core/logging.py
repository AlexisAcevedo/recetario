"""
Configuración de Logging Estructurado.
Usa structlog para logging JSON con contexto enriquecido.
"""
import structlog
import logging
import sys

def filter_secrets(logger, log_method, event_dict):
    """
    OWASP A09: Filtra campos sensibles de los logs para prevenir fuga de información.
    """
    sensitive_keys = {"password", "token", "secret", "authorization", "access_token", "refresh_token", "api_key"}
    for key, value in event_dict.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            event_dict[key] = "***MASKED***"
    return event_dict

def configure_logging():
    """
    Configura structlog para logging estructurado en formato JSON.
    
    Se recomienda llamar esta función al inicio de la aplicación (en main.py).
    """
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            filter_secrets,  # Filtro de seguridad añadido
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )


def get_logger(name: str = __name__):
    """
    Obtiene un logger estructurado.
    
    Args:
        name: Nombre del logger (usualmente __name__ del módulo)
        
    Returns:
        Logger de structlog configurado
        
    Example:
        logger = get_logger(__name__)
        logger.info("user_logged_in", user_id=123, ip="192.168.1.1")
    """
    return structlog.get_logger(name)

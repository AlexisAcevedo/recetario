"""
Configuración de Sentry para Error Tracking.
"""
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.core.config import settings


def init_sentry():
    """
    Inicializa Sentry para error tracking.
    
    Solo se activa si SENTRY_DSN está configurado en el entorno.
    """
    dsn = getattr(settings, 'sentry_dsn', None)
    
    if not dsn:
        # Sentry no configurado, no hacer nada
        return
    
    sentry_sdk.init(
        dsn=dsn,
        environment=getattr(settings, 'environment', 'development'),
        traces_sample_rate=0.1,  # 10% de traces para performance
        profiles_sample_rate=0.1,  # 10% de profiling
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            StarletteIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
        ],
        # No enviar datos sensibles
        send_default_pii=False,
        # Filtrar cookies y headers sensibles
        before_send=filter_sensitive_data,
    )


def filter_sensitive_data(event, hint):
    """
    Filtra datos sensibles antes de enviar a Sentry.
    """
    # Filtrar headers de autorización
    if 'request' in event and 'headers' in event['request']:
        headers = event['request']['headers']
        if 'Authorization' in headers:
            headers['Authorization'] = '[FILTERED]'
        if 'Cookie' in headers:
            headers['Cookie'] = '[FILTERED]'
    
    return event


def capture_exception(error: Exception, **context):
    """
    Captura una excepción con contexto adicional.
    """
    with sentry_sdk.push_scope() as scope:
        for key, value in context.items():
            scope.set_extra(key, value)
        sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = "info", **context):
    """
    Captura un mensaje con contexto adicional.
    """
    with sentry_sdk.push_scope() as scope:
        for key, value in context.items():
            scope.set_extra(key, value)
        sentry_sdk.capture_message(message, level=level)

"""
Módulo de Métricas Prometheus.
Configuración de métricas y endpoint para scraping.
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

# Métricas de autenticación
LOGIN_SUCCESS = Counter(
    'auth_login_success_total',
    'Total de logins exitosos',
    ['method']
)

LOGIN_FAILED = Counter(
    'auth_login_failed_total',
    'Total de logins fallidos',
    ['reason']
)

TOKEN_REFRESH = Counter(
    'auth_token_refresh_total',
    'Total de refresh tokens procesados',
    ['status']
)

# Métricas de HTTP
HTTP_REQUESTS = Counter(
    'http_requests_total',
    'Total de requests HTTP',
    ['method', 'endpoint', 'status']
)

HTTP_REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'Duración de requests HTTP',
    ['method', 'endpoint'],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
)

# Métricas de usuarios
ACTIVE_USERS = Gauge(
    'users_active_total',
    'Total de usuarios activos'
)

ACTIVE_SESSIONS = Gauge(
    'sessions_active_total',
    'Total de sesiones activas'
)


def get_metrics() -> Response:
    """Genera respuesta con métricas en formato Prometheus."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# Helpers para registrar métricas fácilmente
def record_login_success(method: str = "password"):
    """Registra un login exitoso."""
    LOGIN_SUCCESS.labels(method=method).inc()


def record_login_failed(reason: str = "invalid_credentials"):
    """Registra un login fallido."""
    LOGIN_FAILED.labels(reason=reason).inc()


def record_token_refresh(status: str = "success"):
    """Registra un refresh de token."""
    TOKEN_REFRESH.labels(status=status).inc()


def record_http_request(method: str, endpoint: str, status: int, duration: float):
    """Registra una request HTTP."""
    HTTP_REQUESTS.labels(method=method, endpoint=endpoint, status=str(status)).inc()
    HTTP_REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

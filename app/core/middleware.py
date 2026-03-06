import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.metrics import record_http_request


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware para inyectar cabeceras de seguridad HTTP (OWASP A02)
    y registrar métricas de cada request.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()

        response = await call_next(request)

        # Cabeceras de seguridad
        response.headers["Content-Security-Policy"] = "default-src 'none'"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"

        # Métricas HTTP
        duration = time.time() - start_time
        endpoint = request.url.path
        record_http_request(request.method, endpoint, response.status_code, duration)

        return response

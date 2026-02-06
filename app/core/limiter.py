"""
Utilidad de Rate Limiting.
Configuración centralizada de SlowAPI para evitar ciclos de importación.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

# Configuración de Rate Limiting
# Usar key_func=get_remote_address para limitar por IP
limiter = Limiter(key_func=get_remote_address)

# ADR-002: Estrategia de Refresh Tokens

## Estado
✅ Aceptado

## Contexto

Necesitábamos implementar una estrategia de renovación de tokens JWT que balanceara seguridad con experiencia de usuario.

**Opciones evaluadas:**
1. **Refresh tokens en memoria/cliente** - Simple pero inseguro
2. **Refresh tokens en base de datos** - Control total, overhead de DB
3. **Refresh tokens en Redis** - Rápido, pero añade dependencia
4. **JWT de larga duración** - Simple pero riesgoso

## Decisión

**Elegimos almacenar refresh tokens en base de datos (PostgreSQL)** con las siguientes características:

1. **Tabla `sessions`** con refresh_token, user_id, device_info, ip_address
2. **Rotación de tokens**: Nuevo refresh token en cada uso
3. **Revocación**: Campo `is_revoked` para invalidar sesiones
4. **TTL**: 7 días por defecto, configurable
5. **Índice compuesto**: (user_id, is_revoked, expires_at) para queries eficientes

## Consecuencias

### Positivas
- Control total sobre sesiones activas
- Posibilidad de revocar sesiones individuales
- Auditoría de accesos (IP, device)
- Sin dependencias adicionales (ya usamos PostgreSQL)

### Negativas
- Query a DB en cada refresh (mitigado con índices)
- Necesidad de limpieza periódica de tokens expirados

### Mitigaciones
- Índice compuesto reduce latencia a <5ms
- Job de limpieza programable con cron/celery

## Implementación

```python
class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = (
        Index('ix_session_validation', 'user_id', 'is_revoked', 'expires_at'),
    )
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    refresh_token = Column(String(100), unique=True, index=True)
    is_revoked = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True))
```

## Referencias
- [RFC 6749 - OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc6749)
- [JWT Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)

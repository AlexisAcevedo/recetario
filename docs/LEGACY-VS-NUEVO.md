# Legacy vs Nueva Versión - Comparativa

> Documento detallado de las diferencias entre la versión legacy y la nueva arquitectura.

---

## 📊 Tabla Resumen

| Aspecto | Legacy | Nueva Versión | Mejora |
|---------|--------|---------------|--------|
| **Estructura** | Archivos en raíz | Arquitectura por capas | ⭐⭐⭐⭐⭐ |
| **Base de datos** | PostgreSQL/SQLite | PostgreSQL (Supabase) | ⭐⭐⭐⭐ |
| **Validación** | Básica | EmailStr, min/max length | ⭐⭐⭐⭐ |
| **Errores** | HTTPException genéricas | Excepciones personalizadas | ⭐⭐⭐⭐ |
| **Seguridad** | passlib | bcrypt directo + refresh tokens | ⭐⭐⭐⭐⭐ |
| **Tests** | Ninguno | 47 tests automatizados (7 archivos) | ⭐⭐⭐⭐⭐ |
| **Documentación** | README básico | Docs completa en español | ⭐⭐⭐⭐⭐ |
| **Timestamps** | Sin tracking | created_at, updated_at | ⭐⭐⭐⭐ |
| **Config** | Hardcoded | pydantic-settings | ⭐⭐⭐⭐⭐ |
| **Rate Limiting** | Ninguno | slowapi (por IP/usuario) | ⭐⭐⭐⭐ |
| **Observabilidad** | Ninguna | Sentry + logging estructurado | ⭐⭐⭐⭐⭐ |
| **Caché** | Ninguno | Redis con fallback a memoria | ⭐⭐⭐⭐ |

---

## 🔍 Análisis Detallado

### 1. Estructura de Archivos

#### Legacy

```
recetario/
├── config.py          # Todo junto: config + DB
├── models.py          # Modelos
├── schemas.py         # Schemas
├── jwt.py             # Seguridad
├── userService.py     # Servicio
├── login_router.py    # Router
├── user_router.py     # Router
├── me_router.py       # Router
└── main.py            # Entry point
```

#### Nueva Versión

```
recetario/
├── app/
│   ├── core/           # Configuración central
│   │   ├── config.py       # Settings con pydantic
│   │   ├── database.py     # Conexión a BD
│   │   ├── security.py     # JWT + bcrypt
│   │   ├── exceptions.py   # Excepciones custom
│   │   ├── limiter.py      # Rate limiting
│   │   ├── logging.py      # Logging estructurado
│   │   ├── sentry.py       # Error tracking
│   │   └── metrics.py      # Métricas Prometheus
│   ├── models/         # Capa de datos
│   ├── schemas/        # Validación
│   ├── services/       # Lógica de negocio
│   ├── api/v1/         # Capa HTTP
│   └── main.py
└── tests/              # Suite de tests (7 archivos)
```

**¿Por qué es mejor?**

- **Modularidad**: Cada módulo tiene una responsabilidad única
- **Navegabilidad**: Fácil encontrar código por función
- **Escalabilidad**: Agregar entidades es trivial
- **Convención**: Sigue patrones de la industria
- **Observabilidad**: Logging, métricas y error tracking integrados

---

### 2. Configuración

#### Legacy (`config.py`)

```python
# Hardcoded o .env manual
DATABASE_URL = "postgresql://..."
engine = create_engine(DATABASE_URL)
```

**Problemas**:
- Sin validación de variables
- Sin tipado
- Sin valores por defecto documentados

#### Nueva Versión (`app/core/config.py`)

```python
class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
```

**Mejoras**:
- ✅ Validación automática
- ✅ Tipado estático
- ✅ Valores por defecto
- ✅ Documentación integrada
- ✅ Error claro si falta variable

---

### 3. Validación de Datos

#### Legacy (`schemas.py`)

```python
class UserSchema(BaseModel):
    email: str          # ❌ No valida formato
    password: str       # ❌ Sin restricciones
    name: str
    lastname: str
```

#### Nueva Versión (`app/schemas/user.py`)

```python
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserBase(BaseModel):
    email: EmailStr     # ✅ Valida formato email
    name: str = Field(..., min_length=2, max_length=100)
    lastname: str = Field(..., min_length=2, max_length=100)
```

**Mejoras**:
- ✅ EmailStr valida formato de correo
- ✅ Contraseña mínimo 8 caracteres
- ✅ Límites de longitud definidos
- ✅ Mensajes de error claros

---

### 4. Manejo de Errores

#### Legacy

```python
# Errores genéricos dispersos
raise HTTPException(status_code=404, detail="User not found")
raise HTTPException(status_code=400, detail="Invalid credentials")
```

**Problemas**:
- Repetición de código
- Inconsistencia en mensajes
- Difícil de mantener

#### Nueva Versión (`app/core/exceptions.py`)

```python
class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=404,
            detail="Usuario no encontrado"
        )

# Uso:
raise UserNotFoundException()
```

**Mejoras**:
- ✅ Centralizado
- ✅ Consistente
- ✅ Reutilizable
- ✅ Fácil de modificar globalmente

---

### 5. Seguridad (Passwords)

#### Legacy (`jwt.py`)

```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"])

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)
```

**Problema**: passlib tiene incompatibilidades con Python 3.14

#### Nueva Versión (`app/core/security.py`)

```python
import bcrypt

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(
        plain.encode('utf-8'),
        hashed.encode('utf-8')
    )

def get_password_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')[:72]  # Límite bcrypt
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')
```

**Mejoras**:
- ✅ Compatible con Python 3.14
- ✅ Menos dependencias
- ✅ Control explícito del truncado (72 bytes)
- ✅ Rounds configurables

---

### 6. Modelo de Usuario

#### Legacy

```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)
    name = Column(String)
    lastname = Column(String)
```

#### Nueva Versión

```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**Mejoras**:
- ✅ Índices para búsquedas rápidas
- ✅ Longitudes definidas (compatible PostgreSQL)
- ✅ `nullable=False` explícito
- ✅ Timestamps automáticos

---

### 7. Testing

#### Legacy

```
❌ Sin tests
```

#### Nueva Versión

```
tests/
├── conftest.py          # Fixtures (BD en memoria, auth)
├── test_auth.py         # Tests de login y logout
├── test_users.py        # Tests de CRUD de usuarios
├── test_me.py           # Tests de perfil de usuario
├── test_roles.py        # Tests de gestión de roles
├── test_sessions.py     # Tests de sesiones y refresh tokens
├── test_rate_limit.py   # Tests de rate limiting
└── test_e2e_flows.py    # Tests de flujos end-to-end

Total: 47 tests automatizados
```

**Cobertura**:
- Autenticación (login válido/inválido, refresh tokens)
- Creación de usuarios (válido, duplicado, email inválido, contraseña débil)
- Lectura de usuarios (por ID, listado paginado)
- Perfil (get, update, delete)
- Autorización (endpoints protegidos)
- Rate limiting (límites por IP/usuario)
- Roles y permisos
- Flujos E2E completos

---

### 8. Versionado de API

#### Legacy

```python
app.include_router(login_router, prefix="/auth")
app.include_router(user_router, prefix="/user")
```

#### Nueva Versión

```python
app.include_router(api_v1_router, prefix="/api/v1")
```

**Mejoras**:
- ✅ Prefijo `/api/v1` permite versionado futuro
- ✅ Fácil agregar `/api/v2` sin romper existente
- ✅ Estándar de la industria

---

### 9. Rate Limiting

#### Legacy

```
❌ Sin protección contra abuso
```

#### Nueva Versión (`app/core/limiter.py`)

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
```

```python
# En endpoints críticos
@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, ...):
    ...
```

**Mejoras**:
- ✅ Protección contra ataques de fuerza bruta
- ✅ Límites por IP
- ✅ Configurable por endpoint
- ✅ Headers informativos (X-RateLimit-*)

---

### 10. Observabilidad

#### Legacy

```
❌ Sin logging estructurado
❌ Sin error tracking
❌ Sin métricas
```

#### Nueva Versión

**Logging Estructurado** (`app/core/logging.py`):
```python
# Logs en formato JSON para análisis
configure_logging()
```

**Error Tracking** (`app/core/sentry.py`):
```python
# Integración con Sentry
init_sentry()  # DSN desde variables de entorno
```

**Métricas** (`app/core/metrics.py`):
```python
# Endpoint /metrics para Prometheus
get_metrics()
```

**Cache** (`main.py`):
```python
# Redis con fallback automático a memoria
redis = aioredis.from_url("redis://localhost")
FastAPICache.init(RedisBackend(redis))
```

**Mejoras**:
- ✅ Logs estructurados (JSON) para análisis
- ✅ Error tracking automático con Sentry
- ✅ Métricas para Prometheus/Grafana
- ✅ Cache con Redis + fallback inteligente

---

## 📈 Métricas de Mejora

| Métrica | Legacy | Nueva | Cambio |
|---------|--------|-------|--------|
| Archivos Python | 9 | 20+ | +122% (mejor organización) |
| Líneas de código | ~300 | ~900 | +200% (más robusto) |
| Tests | 0 | 47 | ∞ |
| Archivos de test | 0 | 7 | ∞ |
| Validaciones | 0 | 8+ | ∞ |
| Excepciones custom | 0 | 4 | ∞ |
| Docs en español | 0 | 3 archivos | ∞ |
| Módulos de observabilidad | 0 | 4 (logging, sentry, metrics, limiter) | ∞ |

---

## 🎯 Conclusión

La nueva versión representa una evolución significativa del proyecto:

1. **Mejor arquitectura** → Código mantenible y escalable
2. **Más seguro** → Validaciones y hashing mejorado
3. **Más testeable** → Suite completa de tests
4. **Más documentado** → Docs técnica en español
5. **Más profesional** → Estándares de la industria

El código legacy se preserva en `legacy/` para referencia y comparación.

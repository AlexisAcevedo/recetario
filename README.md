# Recetario API

> API REST moderna de gestión de usuarios con autenticación JWT, RBAC, rate limiting y observabilidad

## 🚀 Quick Start

```bash
# Crear entorno virtual
python -m venv env
.\env\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables
cp .env.example .env
# Editar .env con credenciales de Supabase

# Ejecutar
uvicorn app.main:app --reload
```

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| [Documentación Técnica](docs/README.md) | Instalación, configuración, endpoints |
| [Arquitectura](docs/ARQUITECTURA.md) | Diseño del sistema y patrones |
| [ADRs](docs/adr/README.md) | Decisiones arquitectónicas |

## ✨ Funcionalidades

### Seguridad
- ✅ **JWT Authentication** - Access + Refresh tokens con revocación
- ✅ **Validación fuerte de contraseñas** - Mayúsculas, minúsculas, números, símbolos, 12+ chars
- ✅ **Blacklist de contraseñas comunes** - Passwords comunes bloqueadas
- ✅ **Rate Limiting** - 5 req/min en login, 10 req/hora en registro, 100 req/min general
- ✅ **RBAC** - Sistema de roles y permisos
- ✅ **Timing Attack Mitigation** - Respuestas de tiempo constante
- ✅ **Security Headers** - CSP, HSTS, X-Frame-Options, X-Content-Type-Options (OWASP)
- ✅ **CORS Endurecido** - Bloqueo de wildcards en producción

### Performance
- ✅ **Caching** - Redis o fallback a memoria
- ✅ **Índices optimizados** - En email, sessions, tokens
- ✅ **Paginación** - En endpoints de listado

### Observabilidad
- ✅ **Logging estructurado** - Structlog con eventos de seguridad
- ✅ **Métricas Prometheus** - Endpoint `/metrics`
- ✅ **Sentry integration** - Error tracking (opcional)

## 🔐 API Endpoints

**Base URL**: `http://127.0.0.1:8000/api/v1`

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/auth/token` | Login (OAuth2) | ❌ |
| POST | `/auth/refresh` | Renovar access token | ❌ |
| POST | `/auth/logout` | Cerrar sesión | ✅ |
| GET | `/users` | Listar usuarios (paginado) | ✅ |
| POST | `/users` | Crear usuario | ❌ |
| GET | `/users/{id}` | Obtener usuario | ✅ |
| GET | `/me` | Mi perfil | ✅ |
| PUT | `/me` | Actualizar perfil | ✅ |
| DELETE | `/me` | Eliminar cuenta | ✅ |
| GET | `/me/sessions` | Mis sesiones activas | ✅ |
| DELETE | `/me/sessions/{id}` | Revocar sesión | ✅ |
| DELETE | `/me/sessions` | Revocar todas las sesiones | ✅ |
| GET | `/roles` | Listar roles | ✅ Admin |

**Swagger UI**: http://127.0.0.1:8000/docs  
**Health Check**: http://127.0.0.1:8000/health  
**Métricas**: http://127.0.0.1:8000/metrics

## 🧪 Tests

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Solo tests E2E
pytest tests/test_e2e_flows.py -v

# Con coverage
pytest tests/ --cov=app --cov-report=html
```

**Cobertura actual**: 84 tests (8 archivos)

## 📁 Estructura

```
app/
├── api/
│   ├── deps.py         # Dependencias (auth, db, permisos)
│   └── v1/             # Routers v1
│       ├── auth.py     # Login, refresh
│       ├── users.py    # CRUD usuarios
│       ├── me.py       # Perfil actual
│       └── roles.py    # RBAC admin
├── core/
│   ├── config.py       # Settings desde .env
│   ├── database.py     # SQLAlchemy engine
│   ├── security.py     # JWT, hashing, sessions
│   ├── limiter.py      # Rate limiting
│   ├── logging.py      # Structlog config
│   ├── metrics.py      # Prometheus
│   └── sentry.py       # Error tracking
├── models/             # SQLAlchemy models
│   ├── user.py
│   ├── role.py
│   └── session.py
├── schemas/            # Pydantic schemas
└── services/           # Lógica de negocio
    └── user_service.py

tests/
├── conftest.py         # Fixtures
├── test_auth.py
├── test_users.py
├── test_me.py
├── test_roles.py
├── test_sessions.py
├── test_rate_limit.py
├── test_security.py    # Tests OWASP
└── test_e2e_flows.py   # Tests E2E

alembic/
├── env.py              # Configuración async de migraciones
├── script.py.mako      # Template de migraciones
└── versions/           # Migraciones generadas

docs/
├── README.md           # Documentación técnica
├── ARQUITECTURA.md     # Diseño del sistema
└── adr/                # Architecture Decision Records
    ├── 001-bcrypt-vs-argon2.md
    ├── 002-refresh-tokens-strategy.md
    └── 003-sqlalchemy-orm.md
```

## 🛠️ Tech Stack

| Categoría | Tecnología |
|-----------|------------|
| Framework | FastAPI |
| Database | PostgreSQL (Supabase) |
| ORM | SQLAlchemy 2.0 |
| Auth | JWT + bcrypt |
| Validation | Pydantic v2 |
| Testing | pytest |
| Logging | structlog |
| Rate Limit | SlowAPI |
| Cache | fastapi-cache2 |
| Monitoring | Prometheus + Sentry |

## 📋 Variables de Entorno

```env
# Base de datos
DATABASE_URL=postgresql://...

# JWT
SECRET_KEY=tu-secret-key-muy-seguro
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Observabilidad (opcional)
SENTRY_DSN=https://...@sentry.io/...
ENVIRONMENT=development
```

## 📄 Licencia

MIT © 2025

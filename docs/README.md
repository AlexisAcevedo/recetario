# Recetario API - Documentación Técnica

> API REST de gestión de usuarios con autenticación JWT para el sistema de recetario.

---

## 📋 Índice

1. [Descripción del Proyecto](#descripción-del-proyecto)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Instalación](#instalación)
4. [Configuración](#configuración)
5. [Ejecución](#ejecución)
6. [Endpoints de la API](#endpoints-de-la-api)
7. [Tests](#tests)
8. [Estructura del Proyecto](#estructura-del-proyecto)

---

## Descripción del Proyecto

Recetario API es una aplicación backend desarrollada con **FastAPI** que proporciona endpoints para la gestión de usuarios con autenticación basada en **JWT (JSON Web Tokens)**.

### Características principales:

- ✅ **Arquitectura Asíncrona (High Performance)**: Toda la API utiliza `async/await` con FastAPI y SQLAlchemy Asyncio para máxima concurrencia.
- ✅ **Seguridad OWASP 2025**:
    - **Middleware de Cabeceras HTTP**: CSP, HSTS, X-Frame-Options, X-Content-Type-Options.
    - **CORS Endurecido**: Bloqueo automático de wildcards (`*`) en producción.
    - **Validación de Entropía**: `SECRET_KEY` mínima de 32 caracteres requerida.
    - **Logging Seguro**: Filtrado automático de secretos en logs estructurados.
- ✅ **Gestión de Base de Datos**: Migraciones profesionales con **Alembic**.
- ✅ **Autenticación JWT**: Tokens de acceso (Access + Refresh) con revocación.
- ✅ **RBAC (Roles de Usuario)**: Admin, User, Moderator con permisos granulares.
- ✅ **Rate Limiting**: Protección contra abusos (SlowAPI).
- ✅ **Validación Moderna**: Pydantic v2 y SQLAlchemy 2.0 (select style).

---

## Requisitos del Sistema

| Requisito | Versión |
|-----------|---------|
| Python | 3.10+ |
| PostgreSQL | 13+ (o Supabase) |
| pip | 21+ |

### Dependencias principales:

- **FastAPI** - Framework web asíncrono.
- **SQLAlchemy 2.0** - ORM con soporte nativo `ext.asyncio`.
- **asyncpg** - Driver asíncrono para PostgreSQL.
- **aiosqlite** - Driver asíncrono para SQLite (Testing).
- **Alembic** - Herramienta de migraciones de DB.
- **Pydantic v2** - Validación de datos ultrarrápida.

---

## Instalación

### 1. Clonar e Instalar

```bash
git clone <url-del-repositorio>
cd recetario
python -m venv env
# Activar env y luego:
pip install -r requirements.txt
```

### 2. Configuración de Base de Datos

Asegúrate de que tu `DATABASE_URL` sea válida. Alembic la convertirá automáticamente al esquema asíncrono (`postgresql+asyncpg://`).

### 3. Ejecutar Migraciones

Para crear o actualizar las tablas en la base de datos:

```bash
# Crear primera migración (si es nuevo)
alembic revision --autogenerate -m "Initial migration"

# Aplicar migraciones
alembic upgrade head
```

---

## Tests

La suite de pruebas es ahora totalmente asíncrona.

```bash
# Ejecutar todos los tests
pytest tests/ -v
```

### Con cobertura de código

```bash
pytest tests/ --cov=app --cov-report=html
```

### Tests por categoría

```bash
# Solo autenticación
pytest tests/test_auth.py -v

# Solo usuarios
pytest tests/test_users.py -v

# Solo perfil
pytest tests/test_me.py -v
```

---

## Estructura del Proyecto

```
recetario/
├── app/                        # Código fuente principal
│   ├── api/                    # Capa de API (routers)
│   │   ├── deps.py             # Dependencias compartidas
│   │   └── v1/                 # Versión 1 de la API
│   │       ├── auth.py         # Endpoints de autenticación
│   │       ├── users.py        # Endpoints de usuarios
│   │       ├── me.py           # Endpoints de perfil
│   │       ├── roles.py        # Endpoints de RBAC
│   │       └── router.py       # Router agregador
│   ├── core/                   # Configuración central
│   │   ├── config.py           # Variables de entorno
│   │   ├── database.py         # Conexión a BD (AsyncEngine)
│   │   ├── security.py         # JWT y bcrypt
│   │   ├── exceptions.py       # Excepciones HTTP
│   │   ├── middleware.py       # Security headers (OWASP)
│   │   ├── limiter.py          # Rate limiting (SlowAPI)
│   │   ├── logging.py          # Logging estructurado
│   │   ├── metrics.py          # Métricas Prometheus
│   │   └── sentry.py           # Error tracking
│   ├── models/                 # Modelos SQLAlchemy
│   │   ├── user.py             # Modelo de usuario
│   │   ├── role.py             # Modelo de roles (RBAC)
│   │   └── session.py          # Modelo de sesiones
│   ├── schemas/                # Esquemas Pydantic
│   │   ├── user.py             # Schemas de usuario
│   │   ├── role.py             # Schemas de roles
│   │   ├── session.py          # Schemas de sesiones
│   │   └── token.py            # Schemas de token
│   ├── services/               # Lógica de negocio
│   │   └── user_service.py     # Servicio de usuarios
│   └── main.py                 # Punto de entrada
├── tests/                      # Suite de tests
│   ├── conftest.py             # Fixtures
│   ├── test_auth.py            # Tests de auth
│   ├── test_users.py           # Tests de usuarios
│   ├── test_me.py              # Tests de perfil
│   ├── test_roles.py           # Tests de RBAC
│   ├── test_sessions.py        # Tests de sesiones
│   ├── test_rate_limit.py      # Tests de rate limit
│   ├── test_security.py        # Tests de seguridad OWASP
│   └── test_e2e_flows.py       # Tests E2E
├── alembic/                    # Migraciones de BD
│   ├── env.py                  # Configuración async
│   ├── script.py.mako          # Template
│   └── versions/               # Migraciones generadas
├── docs/                       # Documentación
├── legacy/                     # Código original (referencia)
├── alembic.ini                 # Configuración de Alembic
├── .env                        # Variables de entorno
├── .env.example                # Template de variables
├── requirements.txt            # Dependencias
└── README.md                   # Documentación principal
```

---

## Contacto y Soporte

Para reportar bugs o solicitar features, crear un issue en el repositorio.

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

- ✅ **Seguridad OWASP 2025**:
    - **Middleware de Cabeceras HTTP**: CSP, HSTS, X-Frame-Options, X-Content-Type-Options.
    - **CORS Endurecido**: Bloqueo automático de wildcards (`*`) en producción.
    - **Validación de Entropía**: `SECRET_KEY` mínima de 32 caracteres requerida.
    - **Logging Seguro**: Filtrado automático de secretos en logs estructurados.
- ✅ Autenticación JWT con tokens de acceso (Access + Refresh)
- ✅ **RBAC (Roles de Usuario)**: Admin, User, Moderator
- ✅ **Refresh Tokens**: Gestión de sesiones y revocación
- ✅ **Rate Limiting**: Protección contra ataques de fuerza bruta (SlowAPI)
- ✅ CRUD completo de usuarios
- ✅ Validación de datos con Pydantic v2
- ✅ Hasheo seguro de contraseñas con bcrypt
- ✅ Conexión a PostgreSQL (Supabase)
- ✅ Documentación automática con Swagger/OpenAPI
- ✅ Suite de tests con pytest

---

## Requisitos del Sistema

| Requisito | Versión |
|-----------|---------|
| Python | 3.10+ |
| PostgreSQL | 13+ (o Supabase) |
| pip | 21+ |

### Dependencias principales:

- **FastAPI** - Framework web asíncrono
- **SQLAlchemy 2.0** - ORM para base de datos
- **Pydantic v2** - Validación de datos
- **python-jose** - Manejo de JWT
- **bcrypt** - Hasheo de contraseñas
- **structlog** - Logging estructurado y seguro
- **SlowAPI** - Rate limiting

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd recetario
```

### 2. Crear entorno virtual

```bash
# Windows
python -m venv env
.\env\Scripts\activate

# Linux/macOS
python3 -m venv env
source env/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## Configuración

### Variables de entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Base de datos PostgreSQL (Supabase)
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/database

# Seguridad JWT (Mínimo 32 caracteres)
SECRET_KEY=tu-clave-secreta-muy-larga-y-segura-de-32-chars

# Entorno (development | production)
ENVIRONMENT=development

# CORS (Lista separada por comas)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Referencia de variables

| Variable | Descripción | Requerido |
|----------|-------------|-----------|
| `DATABASE_URL` | URL de conexión a PostgreSQL | ✅ |
| `SECRET_KEY` | Clave para firmar tokens JWT (min 32 chars) | ✅ |
| `ENVIRONMENT` | Entorno de ejecución (`production` activa restricciones) | ❌ |
| `CORS_ORIGINS` | Orígenes permitidos (No `*` en producción) | ❌ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duración del token | ❌ (default: 15) |


---

## Ejecución

### Servidor de desarrollo

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en:
- **API**: http://127.0.0.1:8000
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### Servidor de producción

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## Endpoints de la API

### Health Check

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Estado básico |
| GET | `/health` | Estado detallado |

### Autenticación

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/auth/token` | Login (obtener JWT) | ❌ |

**Ejemplo de login:**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/token \
  -d "username=user@email.com&password=mipassword"
```

### Usuarios

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/users` | Listar usuarios | ✅ |
| GET | `/api/v1/users/{id}` | Obtener por ID | ❌ |
| POST | `/api/v1/users` | Crear usuario | ❌ |

**Ejemplo de creación:**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"email":"nuevo@email.com","password":"password123","name":"Juan","lastname":"Pérez"}'
```

### Mi Perfil

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/me` | Mi perfil | ✅ |
| PUT | `/api/v1/me` | Actualizar perfil | ✅ |
| DELETE | `/api/v1/me` | Eliminar cuenta | ✅ |
| GET | `/api/v1/me/sessions` | Listar sesiones activas | ✅ |
| DELETE | `/api/v1/me/sessions` | Cerrar todas las sesiones | ✅ |

### Roles y Permisos (Admin)
| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/roles` | Listar roles | ✅👮 |
| POST | `/api/v1/roles` | Crear rol | ✅👮 |
| POST | `/api/v1/roles/assign` | Asignar rol a usuario | ✅👮 |

> **Nota**: 👮 Requiere rol de Administrador.

### Seguridad Avanzada
| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/auth/refresh` | Renovar access token | ❌ |

**Rate limits aplicados:**
- Login: 5 peticiones/minuto
- Registro: 10 peticiones/hora
- General: 100 peticiones/minuto

---

## Tests

### Ejecutar todos los tests

```bash
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
│   │       └── router.py       # Router agregador
│   ├── core/                   # Configuración central
│   │   ├── config.py           # Variables de entorno
│   │   ├── database.py         # Conexión a BD
│   │   ├── security.py         # JWT y bcrypt
│   │   └── exceptions.py       # Excepciones HTTP
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
│   └── test_rate_limit.py      # Tests de rate limit
├── docs/                       # Documentación
├── legacy/                     # Código original (referencia)
├── .env                        # Variables de entorno
├── .env.example                # Template de variables
├── requirements.txt            # Dependencias
└── README.md                   # Documentación principal
```

---

## Contacto y Soporte

Para reportar bugs o solicitar features, crear un issue en el repositorio.

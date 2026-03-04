# Arquitectura del Sistema

> Guía de arquitectura de Recetario API

---

## 📐 Visión General

La aplicación sigue una **arquitectura por capas** (Layered Architecture), separando responsabilidades en módulos independientes.

```
┌─────────────────────────────────────────┐
│              Clientes                    │
│        (Frontend, Postman, etc.)        │
└─────────────────┬───────────────────────┘
                  │ HTTP (Security Headers)
┌─────────────────▼───────────────────────┐
│         Middleware Layer (Global)        │
│    Auth │ CORS │ Security Headers        │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           API Layer (Routers)            │
│      auth.py │ users.py │ me.py         │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Service Layer (Lógica)           │
│            user_service.py               │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          Model Layer (Datos)             │
│             user.py (ORM)                │
└─────────────────┬───────────────────────┘
                  │ SQLAlchemy 2.0
┌─────────────────▼───────────────────────┐
│         PostgreSQL (Supabase)            │
└─────────────────────────────────────────┘
```

---

## 🏗️ Capas del Sistema

### 1. Middleware Layer (`app/core/middleware.py`)

**Responsabilidad**: Interceptar peticiones globalmente para aplicar políticas de seguridad.

- **Security Headers**: Inyecta cabeceras OWASP (CSP, HSTS, X-Frame-Options).
- **CORS Endurecido**: Gestiona orígenes permitidos con validación de entorno.
- **Rate Limiting**: (SlowAPI) Previene DoS y fuerza bruta.

### 2. API Layer (`app/api/`)

**Responsabilidad**: Manejo de requests HTTP, validación de entrada, serialización de respuestas.

| Archivo | Descripción |
|---------|-------------|
| `deps.py` | Dependencias compartidas (get_db, get_current_user) |
| `v1/auth.py` | Endpoints de autenticación |
| `v1/users.py` | Endpoints CRUD de usuarios |
| `v1/me.py` | Endpoints del perfil actual |
| `v1/router.py` | Agregador de routers |

**Principios**:
- Los routers NO contienen lógica de negocio
- Delegan a servicios para operaciones
- Manejan solo HTTP y validación

### 3. Service Layer (`app/services/`)

**Responsabilidad**: Lógica de negocio, reglas de dominio.

| Archivo | Funciones |
|---------|-----------|
| `user_service.py` | CRUD, autenticación, validaciones |

**Principios**:
- Contiene TODA la lógica de negocio
- Agnóstico al framework (no conoce FastAPI)
- Fácil de testear unitariamente

### 4. Model Layer (`app/models/`)

**Responsabilidad**: Definición de entidades de base de datos.

| Archivo | Tabla |
|---------|-------|
| `user.py` | `users` |
| `role.py` | `roles` (RBAC) |
| `session.py` | `sessions` (Refresh Tokens) |

**Principios**:
- Solo definición de tablas
- Sin lógica de negocio
- Mapeo ORM con SQLAlchemy 2.0

### 5. Schema Layer (`app/schemas/`)

**Responsabilidad**: Validación de datos con Pydantic v2.

| Archivo | Esquemas |
|---------|----------|
| `user.py` | UserCreate, UserUpdate, UserResponse |
| `token.py` | Token, TokenData |
| `session.py` | SessionResponse, TokenPair |

### 6. Core Layer (`app/core/`)

**Responsabilidad**: Configuración central y utilidades transversales.

| Archivo | Función |
|---------|---------|
| `config.py` | Variables de entorno (con validación de entropía) |
| `database.py` | Conexión a PostgreSQL |
| `security.py` | JWT y bcrypt |
| `logging.py` | Logging estructurado con enmascaramiento de secretos (OWASP A09) |
| `middleware.py` | Implementación de cabeceras de seguridad |

---

## 🔄 Flujo de una Request

```
1. Cliente hace POST /api/v1/users
        │
2. Middleware inyecta cabeceras de seguridad
        │
3. FastAPI valida UserCreate (schema Pydantic v2)
        │
4. Router recibe request validada
        │
5. Router inyecta Session (deps.py)
        │
6. Router llama user_service.create_user()
        │
7. Service hashea password, crea User
        │
8. Service hace commit a PostgreSQL
        │
9. Service retorna User
        │
10. Router serializa a UserResponse
        │
11. Cliente recibe JSON + Security Headers
```

---

### 🔐 Seguridad y Autenticación (OWASP 2025)
1. **Defensa en Profundidad**: Aplicación de múltiples capas de seguridad (Middleware, ORM, Pydantic).
2. **Login**: Usuario envía credenciales -> Recibe `access_token` (JWT corta duración) y `refresh_token`.
3. **Uso de API**: Cliente envía `Authorization: Bearer <access_token>`.
4. **Renovación**: Cuando `access_token` expira, cliente usa `refresh_token` en endpoint `/refresh` para obtener nuevo par.
5. **Logging Seguro**: Implementación de `filter_secrets` para evitar fuga de PII y secretos en logs.
6. **Validación de Secretos**: Requisito de entropía alta para `SECRET_KEY` (min 32 chars).
7. **CORS**: Configuración restrictiva; falla si se usa `*` en producción.
8. **RBAC**: Middleware verifica roles en endpoints protegidos (ej: `admin`, `moderator`).
9. **Rate Limiting**: `SlowAPI` limita peticiones por IP para prevenir abusos.

---

## 🧩 Patrones de Diseño Utilizados

| Patrón | Uso |
|--------|-----|
| **Repository** | user_service abstrae acceso a datos |
| **Dependency Injection** | FastAPI Depends() para DB y auth |
| **Factory** | SessionLocal crea sesiones |
| **DTO** | Pydantic schemas como DTOs |

---

## 📦 Decisiones de Diseño

### ¿Por qué arquitectura por capas?

- **Separación de responsabilidades**: Cada capa tiene una función clara
- **Testabilidad**: Servicios testeables sin HTTP
- **Mantenibilidad**: Cambios aislados en cada capa
- **Escalabilidad**: Fácil agregar nuevas entidades

### ¿Por qué Supabase?

- **Tier gratuito**: Ideal para proyectos personales
- **PostgreSQL real**: No SQLite limitado
- **Dashboard incluido**: Administración visual
- **Escalable**: Crece con el proyecto

### ¿Por qué bcrypt directo?

- **Compatibilidad**: passlib tiene issues con Python 3.14
- **Simplicidad**: Menos dependencias
- **Seguridad**: bcrypt es el estándar de la industria

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

**Responsabilidad**: Interceptar peticiones globalmente para aplicar políticas de seguridad de forma no bloqueante.

- **Security Headers**: Inyecta cabeceras OWASP (CSP, HSTS, X-Frame-Options).
- **CORS Endurecido**: Gestiona orígenes permitidos con validación de entorno.
- **Rate Limiting**: (SlowAPI) Previene DoS y fuerza bruta.

### 2. API Layer (`app/api/`)

**Responsabilidad**: Manejo de requests HTTP **asíncronas**, validación de entrada, serialización de respuestas.

| Archivo | Descripción |
|---------|-------------|
| `deps.py` | Dependencias asíncronas (`get_db`, `get_current_user`). |
| `v1/auth.py` | Endpoints de autenticación asíncronos. |
| `v1/users.py` | Endpoints CRUD de usuarios asíncronos. |
| `v1/me.py` | Endpoints del perfil actual asíncronos. |
| `v1/roles.py` | Gestión de RBAC asíncrona. |

### 3. Service Layer (`app/services/`)

**Responsabilidad**: Lógica de negocio mediante corrutinas (`async def`).

| Archivo | Funciones |
|---------|-----------|
| `user_service.py` | CRUD, autenticación, mitigación de timing attacks con `asyncio.sleep`. |

### 4. Model Layer (`app/models/`)

**Responsabilidad**: Entidades de DB compatibles con SQLAlchemy 2.0 y Async.

- **Eager Loading**: Uso de `lazy="selectin"` para evitar errores de `MissingGreenlet` al acceder a relaciones en contextos asíncronos.

### 5. Core Layer (`app/core/`)

**Responsabilidad**: Configuración y motores asíncronos.

- **`database.py`**: Motor `AsyncEngine` y `AsyncSessionLocal`.
- **`security.py`**: Utilidades de JWT y bcrypt (ejecutadas de forma eficiente).
- **`logging.py`**: Logging JSON con enmascaramiento.

---

### 🔐 Seguridad y Autenticación (OWASP 2025)
1. **Defensa en Profundidad**: Múltiples capas de seguridad asíncronas.
2. **Concurrencia Segura**: Uso de `asyncio.sleep` para timing attacks sin bloquear el hilo principal.
3. **Eager Relationship Loading**: Configuración de modelos para cargar relaciones automáticamente en async.
4. **Logging Seguro**: Implementación de `filter_secrets` para evitar fuga de PII y secretos.
5. **Validación de Secretos**: Requisito de entropía alta para `SECRET_KEY` (min 32 chars).
6. **Rate Limiting**: Integrado nativamente en el flujo asíncrono de FastAPI.

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

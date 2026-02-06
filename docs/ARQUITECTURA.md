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
                  │ HTTP
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
                  │ SQLAlchemy
┌─────────────────▼───────────────────────┐
│         PostgreSQL (Supabase)            │
└─────────────────────────────────────────┘
```

---

## 🏗️ Capas del Sistema

### 1. API Layer (`app/api/`)

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

### 2. Service Layer (`app/services/`)

**Responsabilidad**: Lógica de negocio, reglas de dominio.

| Archivo | Funciones |
|---------|-----------|
| `user_service.py` | CRUD, autenticación, validaciones |

**Principios**:
- Contiene TODA la lógica de negocio
- Agnóstico al framework (no conoce FastAPI)
- Fácil de testear unitariamente

### 3. Model Layer (`app/models/`)

**Responsabilidad**: Definición de entidades de base de datos.

| Archivo | Tabla |
|---------|-------|
| `user.py` | `users` |

**Principios**:
- Solo definición de tablas
- Sin lógica de negocio
- Mapeo ORM con SQLAlchemy

### 4. Schema Layer (`app/schemas/`)

**Responsabilidad**: Validación de datos con Pydantic.

| Archivo | Esquemas |
|---------|----------|
| `user.py` | UserCreate, UserUpdate, UserResponse |
| `token.py` | Token, TokenData |

### 5. Core Layer (`app/core/`)

**Responsabilidad**: Configuración central y utilidades transversales.

| Archivo | Función |
|---------|---------|
| `config.py` | Variables de entorno |
| `database.py` | Conexión a PostgreSQL |
| `security.py` | JWT y bcrypt |
| `exceptions.py` | Excepciones HTTP personalizadas |

---

## 🔄 Flujo de una Request

```
1. Cliente hace POST /api/v1/users
        │
2. FastAPI valida UserCreate (schema)
        │
3. Router recibe request validada
        │
4. Router inyecta Session (deps.py)
        │
5. Router llama user_service.create_user()
        │
6. Service hashea password, crea User
        │
7. Service hace commit a PostgreSQL
        │
8. Service retorna User
        │
9. Router serializa a UserResponse
        │
10. Cliente recibe JSON
```

---

### 🔐 Seguridad y Autenticación
1. **Login**: Usuario envía credenciales -> Recibe `access_token` (JWT corta duración) y `refresh_token`.
2. **Uso de API**: Cliente envía `Authorization: Bearer <access_token>`.
3. **Renovación**: Cuando `access_token` expira, cliente usa `refresh_token` en endpoint `/refresh` para obtener nuevo par.
4. **Logout**: Cliente revoca sesión en `/me/sessions`.
5. **RBAC**: Middleware verifica roles en endpoints protegidos (ej: `admin`, `moderator`).
6. **Rate Limiting**: `SlowAPI` limita peticiones por IP para prevenir abusos.

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

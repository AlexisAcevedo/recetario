# Recetario API

API REST de gestión de usuarios con autenticación JWT para el sistema de recetario.

## 🚀 Quick Start

```bash
# Clonar y entrar al proyecto
cd recetario

# Crear entorno virtual
python -m venv env
.\env\Scripts\activate  # Windows
source env/bin/activate # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de Supabase

# Ejecutar servidor
uvicorn app.main:app --reload
```

## 📚 Documentación API

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 🔐 Endpoints

### Autenticación
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/auth/token` | Login (obtener JWT) |

### Usuarios
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/users` | Listar usuarios (auth) |
| GET | `/api/v1/users/{id}` | Obtener usuario por ID |
| POST | `/api/v1/users` | Crear usuario |

### Mi Perfil
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/me` | Mi perfil (auth) |
| PUT | `/api/v1/me` | Actualizar perfil (auth) |
| DELETE | `/api/v1/me` | Eliminar cuenta (auth) |

## 🧪 Tests

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=app
```

## 📁 Estructura

```
recetario/
├── app/
│   ├── api/v1/          # Routers
│   ├── core/            # Config, security, DB
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   └── services/        # Business logic
├── tests/               # Test suite
├── legacy/              # Código original (referencia)
└── requirements.txt
```

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.128+
- **Database**: PostgreSQL (Supabase)
- **ORM**: SQLAlchemy 2.0
- **Auth**: JWT + bcrypt
- **Validation**: Pydantic 2.0
- **Tests**: pytest + httpx

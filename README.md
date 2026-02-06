# Recetario API

> API REST de gestión de usuarios con autenticación JWT

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
| [Legacy vs Nuevo](docs/LEGACY-VS-NUEVO.md) | Comparativa de versiones |

## 🔐 API Endpoints

**Base URL**: `http://127.0.0.1:8000/api/v1`

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/auth/token` | Login |
| GET | `/users` | Listar usuarios |
| POST | `/users` | Crear usuario |
| GET | `/me` | Mi perfil |
| PUT | `/me` | Actualizar perfil |
| DELETE | `/me` | Eliminar cuenta |

**Swagger UI**: http://127.0.0.1:8000/docs

## 🧪 Tests

```bash
pytest tests/ -v
```

## 📁 Estructura

```
app/
├── api/v1/     # Routers
├── core/       # Config, DB, Security
├── models/     # SQLAlchemy
├── schemas/    # Pydantic
└── services/   # Lógica de negocio
```

## 🛠️ Tech Stack

FastAPI • SQLAlchemy • PostgreSQL (Supabase) • JWT • bcrypt • Pydantic

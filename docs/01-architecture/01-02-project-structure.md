# Estructura del Proyecto

**Versión**: 1.0  
**Fecha**: Noviembre 2024  
**Estado**: Vigente  
**Autor(es)**: Equipo de Desarrollo Goluti

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Estructura de Directorios](#estructura-de-directorios)
3. [Estructura por Capa](#estructura-por-capa)
4. [Convenciones de Nomenclatura](#convenciones-de-nomenclatura)
5. [Archivos de Configuración](#archivos-de-configuración)
6. [Referencias](#referencias)

---

## Introducción

Este documento describe la organización de archivos y directorios del proyecto **Goluti Backend Platform**, explicando el propósito de cada carpeta y archivo principal.

---

## Estructura de Directorios

### Vista General

```
platform/
├── docs/                           # Documentación del proyecto
├── env/                            # Entorno virtual de Python
├── migrations/                     # Migraciones de base de datos SQL
├── src/                           # Código fuente principal
│   ├── core/                      # Componentes transversales
│   ├── domain/                    # Lógica de dominio
│   └── infrastructure/            # Implementaciones de infraestructura
├── main.py                        # Punto de entrada de la aplicación
├── pipfiles.txt                   # Dependencias de Python
├── README.md                      # Documentación básica
├── .env.pc                        # Variables de entorno local
├── .env.qa                        # Variables de entorno QA
├── .env.prod                      # Variables de entorno producción
├── docker-compose.*.yml           # Configuraciones Docker
├── Dockerfile.*                   # Archivos Docker
├── buildspec.*.yml                # Configuración CI/CD AWS
└── Dockerrun.aws.*.json           # Configuración Elastic Beanstalk
```

---

## Estructura por Capa

### 1. Core (`src/core/`)

Componentes transversales utilizados por todas las capas:

```
src/core/
├── __init__.py
├── config.py                      # Configuración principal
│
├── classes/                       # Clases auxiliares
│   ├── async_message.py           # Gestión de mensajes localizados
│   ├── bearer.py                  # Autenticación Bearer
│   ├── password.py                # Hashing de contraseñas
│   └── token.py                   # JWT tokens
│
├── enums/                         # Tipos enumerados
│   ├── condition_type.py          # Condiciones de filtros
│   ├── context.py                 # Contextos
│   ├── keys_message.py            # Keys de mensajes
│   ├── language.py                # Idiomas
│   ├── layer.py                   # Capas de arquitectura
│   ├── message_type.py            # Tipos de mensaje
│   ├── notification_type.py       # Tipos de notificación
│   ├── permission_type.py         # Tipos de permisos
│   └── response_type.py           # Tipos de respuesta
│
├── methods/                       # Métodos utilitarios
│   ├── apply_memory_filters.py    # Filtros en memoria
│   ├── build_alias_map.py         # Mapas de alias
│   ├── get_config.py              # Extracción de config
│   ├── get_filter.py              # Construcción de filtros
│   └── get_filter_with_alias.py   # Filtros con alias
│
├── middleware/                    # Middleware FastAPI
│   ├── cors_app.py                # CORS
│   ├── redirect_to_docs.py        # Redirección a docs
│   └── user_rate_limit_middleware.py  # Rate limiting
│
├── models/                        # Modelos compartidos
│   ├── access_token.py            # Access token JWT
│   ├── access_token_api.py        # API token
│   ├── base.py                    # Modelo base
│   ├── config.py                  # Config
│   ├── filter.py                  # Filtros y paginación
│   ├── message.py                 # Mensajes
│   ├── params_ws.py               # Parámetros WebSocket
│   ├── response.py                # Response wrapper
│   └── ws_request.py              # WebSocket request
│
└── wrappers/                      # Decoradores (AOP)
    ├── check_permissions.py       # Verificación de permisos
    ├── check_roles.py             # Verificación de roles
    └── execute_transaction.py     # Tracking de transacciones
```

### 2. Domain (`src/domain/`)

Lógica de negocio y modelos de dominio:

```
src/domain/
├── __init__.py
│
├── models/                        # Modelos de dominio
│   ├── entities/                  # Modelos de entidades CRUD
│   │   ├── user/
│   │   │   ├── user.py            # Modelo principal
│   │   │   ├── user_save.py       # Modelo para crear
│   │   │   ├── user_update.py     # Modelo para actualizar
│   │   │   ├── user_read.py       # Modelo para leer
│   │   │   ├── user_delete.py     # Modelo para eliminar
│   │   │   └── index.py           # Exportaciones
│   │   ├── company/
│   │   ├── platform/
│   │   ├── location/
│   │   ├── language/
│   │   ├── currency/
│   │   ├── country/
│   │   ├── menu/
│   │   ├── permission/
│   │   ├── rol/
│   │   ├── api_token/
│   │   ├── translation/
│   │   ├── currency_location/
│   │   ├── menu_permission/
│   │   ├── rol_permission/
│   │   └── user_location_rol/
│   │
│   └── business/                  # Modelos de lógica de negocio
│       └── auth/
│           ├── login/
│           │   ├── auth_login_request.py
│           │   ├── auth_login_response.py
│           │   ├── auth_initial_user_data.py
│           │   ├── auth_locations.py
│           │   ├── auth_currencies_by_location.py
│           │   ├── auth_user_role_and_permissions.py
│           │   ├── companies_by_user.py
│           │   ├── auth_menu.py
│           │   └── index.py
│           ├── logout/
│           ├── refresh_token/
│           └── create_api_token/
│
└── services/                      # Servicios de dominio
    ├── repositories/              # Interfaces de repositorios
    │   ├── entities/
    │   │   ├── i_user_repository.py
    │   │   ├── i_company_repository.py
    │   │   ├── i_platform_repository.py
    │   │   └── ... (una por entidad)
    │   └── business/
    │       └── ... (si aplica)
    │
    └── use_cases/                 # Casos de uso
        ├── entities/              # Use cases de entidades
        │   ├── user/
        │   │   ├── user_save_use_case.py
        │   │   ├── user_update_use_case.py
        │   │   ├── user_list_use_case.py
        │   │   ├── user_read_use_case.py
        │   │   ├── user_delete_use_case.py
        │   │   └── index.py
        │   ├── company/
        │   ├── platform/
        │   └── ... (uno por entidad)
        │
        └── business/              # Use cases de lógica de negocio
            └── auth/
                ├── login/
                │   ├── auth_login_use_case.py
                │   ├── auth_validate_user_use_case.py
                │   ├── auth_initial_user_data_use_case.py
                │   ├── auth_locations_use_case.py
                │   ├── auth_currencies_use_case.py
                │   ├── auth_languages_use_case.py
                │   ├── auth_menu_use_case.py
                │   ├── auth_user_role_and_permissions.py
                │   └── companies_by_user_use_case.py
                ├── logout/
                ├── refresh_token/
                └── create_api_token/
```

### 3. Infrastructure (`src/infrastructure/`)

Implementaciones de infraestructura:

```
src/infrastructure/
├── __init__.py
│
├── database/                      # Capa de persistencia
│   ├── config/
│   │   └── async_config_db.py     # Configuración de BD asíncrona
│   │
│   ├── entities/                  # Modelos SQLAlchemy
│   │   ├── user_entity.py
│   │   ├── company_entity.py
│   │   ├── platform_entity.py
│   │   └── ... (uno por entidad)
│   │
│   ├── mappers/                   # Mapeo DB ↔ Domain
│   │   ├── user_mapper.py
│   │   ├── company_mapper.py
│   │   └── ... (uno por entidad)
│   │
│   └── repositories/              # Implementaciones de repositorios
│       ├── entities/
│       │   ├── user_repository.py
│       │   ├── company_repository.py
│       │   └── ... (uno por entidad)
│       └── business/
│           └── mappers/
│               └── auth/
│                   └── login/
│                       └── login_mapper.py
│
└── web/                           # Capa de presentación HTTP
    ├── routes/
    │   ├── route.py               # Configurador de rutas de entidades
    │   ├── route_business.py      # Configurador de rutas de negocio
    │   └── route_websockets.py    # Configurador de WebSockets
    │
    ├── controller/
    │   ├── entities/              # Controladores de entidades
    │   │   ├── user_controller.py
    │   │   ├── company_controller.py
    │   │   └── ... (uno por entidad)
    │   └── business/              # Controladores de negocio
    │       └── auth_controller.py
    │
    ├── entities_routes/           # Routers FastAPI de entidades
    │   ├── user_router.py
    │   ├── company_router.py
    │   └── ... (uno por entidad)
    │
    ├── business_routes/           # Routers FastAPI de negocio
    │   └── auth_router.py
    │
    └── websockets_routes/         # Routers WebSocket
        └── example_router.py
```

---

## Convenciones de Nomenclatura

### Archivos y Módulos

| Tipo | Patrón | Ejemplo |
|------|--------|---------|
| **Modelos de Dominio** | `{entity}.py`, `{entity}_{operation}.py` | `user.py`, `user_save.py` |
| **Use Cases** | `{entity}_{operation}_use_case.py` | `user_save_use_case.py` |
| **Repositorios Interface** | `i_{entity}_repository.py` | `i_user_repository.py` |
| **Repositorios Impl** | `{entity}_repository.py` | `user_repository.py` |
| **Entities SQLAlchemy** | `{entity}_entity.py` | `user_entity.py` |
| **Mappers** | `{entity}_mapper.py` | `user_mapper.py` |
| **Controllers** | `{entity}_controller.py` | `user_controller.py` |
| **Routers** | `{entity}_router.py` | `user_router.py` |

### Clases

| Tipo | Patrón | Ejemplo |
|------|--------|---------|
| **Modelo Dominio** | `{Entity}` | `User` |
| **Modelo Operación** | `{Entity}{Operation}` | `UserSave`, `UserUpdate` |
| **Use Case** | `{Entity}{Operation}UseCase` | `UserSaveUseCase` |
| **Repository Interface** | `I{Entity}Repository` | `IUserRepository` |
| **Repository Impl** | `{Entity}Repository` | `UserRepository` |
| **Entity SQLAlchemy** | `{Entity}Entity` | `UserEntity` |
| **Controller** | `{Entity}Controller` | `UserController` |

### Variables y Métodos

- **snake_case**: Para variables, métodos y funciones
- **SCREAMING_SNAKE_CASE**: Para constantes
- **PascalCase**: Para clases

```python
# Variables
user_repository = UserRepository()
access_token = "..."

# Constantes
MAX_RETRY_ATTEMPTS = 3

# Métodos
async def save(self, config: Config, params: UserSave):
    pass

# Clases
class UserSaveUseCase:
    pass
```

### Convención Entity ↔ Tabla de Base de Datos

**Regla Importante**: Los nombres de las entidades del dominio corresponden **exactamente** a los nombres de las tablas en PostgreSQL.

| Entity (Python) | Tabla (PostgreSQL) | Schema |
|-----------------|-------------------|--------|
| `User` | `user` | `platform` |
| `Company` | `company` | `platform` |
| `UserLocationRol` | `user_location_rol` | `platform` |
| `CurrencyLocation` | `currency_location` | `platform` |

**Transformación de nombres:**
- **Python (Código)**: PascalCase → `User`, `UserLocationRol`
- **Base de Datos**: snake_case → `user`, `user_location_rol`
- **Conversión**: Se mantiene la correspondencia directa, solo cambia el formato

**Ejemplo:**
```python
# Entity SQLAlchemy
class UserEntity(Base):
    __tablename__ = "user"  # ← Mismo nombre que la entidad en snake_case
    __table_args__ = {"schema": "platform"}
```

Esta convención garantiza:
- ✅ Consistencia entre código y base de datos
- ✅ Fácil mapeo mental entre capas
- ✅ Sin ambigüedades en nombres
- ✅ Mantenibilidad del código

---

## Archivos de Configuración

### Punto de Entrada: `main.py`

```python
from fastapi import FastAPI
from src.core.config import settings
from src.infrastructure.web.routes.route import Route
from src.infrastructure.web.routes.route_business import RouteBusiness
from src.infrastructure.web.routes.route_websockets import RouteWebsockets

app = FastAPI(
    title=settings.project_name,
    description=settings.project_description,
    version=settings.project_version,
)

# Configurar middleware
# ...

# Configurar rutas
RouteBusiness.set_routes(app)
Route.set_routes(app)
RouteWebsockets.set_routes(app)
```

### Variables de Entorno

#### `.env.pc` (Desarrollo Local)
```bash
ENV=pc
APP_ENVIRONMENT=development
PROJECT_NAME=Goluti Platform API
PROJECT_VERSION=1.0.0
DATABASE_HOST=localhost
DATABASE_PORT=5432
# ...
```

#### `.env.qa` (QA/Staging)
```bash
ENV=qa
APP_ENVIRONMENT=qa
# ...
```

#### `.env.prod` (Producción)
```bash
ENV=prod
APP_ENVIRONMENT=production
# ...
```

### Dependencias: `pipfiles.txt`

```text
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
sqlalchemy==2.0.23
asyncpg==0.29.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
```

### Docker

#### `docker-compose.local.yml`
Configuración para desarrollo local con Docker.

#### `docker-compose.qa.yml`
Configuración para ambiente QA.

#### `docker-compose.prod.yml`
Configuración para producción.

#### `Dockerfile.local`, `Dockerfile.qa`, `Dockerfile.prod`
Archivos Docker específicos por ambiente.

### CI/CD

#### `buildspec.yml`, `buildspec.qa.yml`, `buildspec.prod.yml`
Configuración para AWS CodeBuild.

#### `Dockerrun.aws.json`, `Dockerrun.aws.qa.json`, `Dockerrun.aws.prod.json`
Configuración para AWS Elastic Beanstalk.

---

## Migraciones

```
migrations/
├── changelog-v1.sql
├── changelog-v2.sql
├── changelog-v3.sql
├── ...
└── changelog-v24.sql
```

Archivos SQL ejecutados secuencialmente para evolucionar el esquema de base de datos.

---

## Referencias

- **[01-00] Architecture Overview**: Visión general de la arquitectura
- **[01-03] Layers and Responsibilities**: Responsabilidades de cada capa
- **[02-00] Entity Flow Overview**: Estructura del flujo de entidades
- **[03-00] Business Flow Overview**: Estructura del flujo de negocio

---

## Historial de Cambios

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0 | Nov 2024 | Creación inicial | Equipo de Desarrollo Goluti |

---

**Fin del Documento**


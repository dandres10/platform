# Especificación de Flujo: List Users External

**Documento:** 07-04-list-users-external-flow.md  
**Versión:** 2.2  
**Fecha:** Noviembre 11, 2024  
**Autor:** Equipo de Desarrollo Goluti

---

## Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Objetivo del Flujo](#objetivo-del-flujo)
3. [Contexto de Negocio](#contexto-de-negocio)
4. [Diagrama de Flujo](#diagrama-de-flujo)
5. [Componentes Involucrados](#componentes-involucrados)
6. [Endpoints API](#endpoints-api)
7. [Modelos de Datos](#modelos-de-datos)
8. [Implementación con SQLAlchemy](#implementación-con-sqlalchemy)
9. [Paginación y Filtros](#paginación-y-filtros)
10. [Manejo de Errores](#manejo-de-errores)
11. [Seguridad](#seguridad)
12. [Ejemplos de Uso](#ejemplos-de-uso)
13. [Testing](#testing)
14. [Consideraciones Técnicas](#consideraciones-técnicas)
15. [Historial de Cambios](#historial-de-cambios)

---

## Resumen Ejecutivo

Este documento especifica el flujo de negocio para **listar usuarios externos** en el sistema Goluti Backend Platform. El servicio permite consultar todos los usuarios externos (clientes) registrados en el sistema, obteniendo información completa del usuario y su configuración de platform (excepto password).

**Características principales:**
- ✅ Consulta paginada de usuarios externos (clientes)
- ✅ Uso directo de SQLAlchemy con consulta optimizada
- ✅ JOIN entre tablas `user`, `platform` y validación con `user_location_rol`
- ✅ **Doble validación de seguridad**: 
  - `platform.location_id IS NULL` (identificador principal)
  - `user_location_rol.id IS NULL` (validación que NO existe registro)
- ✅ Retorna información completa del usuario + platform sin password
- ✅ Soporte de filtros avanzados (nombre, email, identification, etc.)
- ✅ Requiere autenticación y permisos de lectura

**⚠️ Importante:** Los usuarios externos **NO tienen registro** en `user_location_rol`. Se identifican porque en la tabla `platform` el campo `location_id` es `NULL` **Y** NO tienen ningún registro en `user_location_rol`.

---

## Objetivo del Flujo

Permitir consultar de manera eficiente todos los usuarios externos (clientes) registrados en el sistema, mostrando sus datos personales y configuración de platform (excepto información sensible como el password).

### Alcance

**En alcance:**
- ✅ Sistema de filtros **flexible y genérico** usando `filters`
- ✅ **El desarrollador puede filtrar por CUALQUIER campo del response** (`UserExternalItem`)
- ✅ Todos los campos retornados son filtrables: IDs, strings, booleans, fechas
- ✅ Query con JOIN entre `user`, `platform` y LEFT JOIN con `user_location_rol`
- ✅ **Doble filtro de seguridad**:
  - `platform.location_id IS NULL` (identificador principal)
  - `user_location_rol.id IS NULL` (validación adicional de seguridad)
- ✅ Paginación configurable con `all_data` flag:
  - `all_data=false`: Aplica paginación (skip/limit)
  - `all_data=true`: Retorna todos los registros
- ✅ Filtros aplicados en memoria usando `apply_memory_filters` y `build_alias_map`
- ✅ Retornar información completa del usuario + platform (sin password)
- ✅ Requiere autenticación y permiso READ

**Fuera de alcance:**
- ❌ Usuarios internos (empleados/colaboradores)
- ❌ Información de roles (los usuarios externos no tienen roles)
- ❌ Información de ubicaciones (los usuarios externos no tienen location_id)
- ❌ Modificación de datos (solo lectura)
- ❌ Información del password (nunca se expone)

---

## Contexto de Negocio

### Problema

Los administradores necesitan visualizar y gestionar los usuarios externos (clientes) registrados en la plataforma para:
- Gestionar base de clientes
- Verificar registros de usuarios
- Auditar información de clientes
- Soporte al cliente
- Análisis de usuarios registrados

**Regla de Negocio:** Los usuarios externos se registran **SOLO** en las tablas `user` y `platform`. Se identifican mediante **doble validación**:
1. En la tabla `platform`, el campo `location_id` es `NULL`
2. **NO existe** ningún registro en la tabla `user_location_rol` para ese usuario

### Solución

Crear un endpoint `/auth/users-external` que:
1. Consulta con JOIN entre `user` y `platform`, LEFT JOIN con `user_location_rol`
2. **Doble filtro de seguridad**:
   - `platform.location_id IS NULL`
   - `user_location_rol.id IS NULL` (garantiza que NO tiene registros en user_location_rol)
3. Retorna lista paginada con información de usuarios + configuración de platform
4. Excluye el password del usuario
5. Sistema de filtros genérico y flexible
6. Filtros aplicados en memoria usando `apply_memory_filters` y `build_alias_map`

### Beneficios

- ✅ **Performance**: Query optimizado con JOINs necesarios
- ✅ **Seguridad Robusta**: 
  - Password nunca se expone
  - Doble validación para garantizar que son usuarios externos
  - Imposible mezclar usuarios internos con externos
- ✅ **Flexibilidad Total**: Cualquier campo del response es filtrable automáticamente
- ✅ **Escalabilidad**: Paginación para grandes volúmenes
- ✅ **Completitud**: Información completa de usuarios externos + platform
- ✅ **Separación clara**: Solo usuarios externos, sin mezclar con internos

---

## Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────────┐
│             INICIO: List Users External                         │
│           POST /auth/users-external                              │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│     1. VALIDAR AUTENTICACIÓN Y PERMISOS                         │
│  - Token JWT válido                                             │
│  - Permiso: PERMISSION_TYPE.READ                                │
│  ├─ Si falla → HTTP 401/403                                     │
│  └─ Si OK → Continuar                                           │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│     2. VALIDAR PARÁMETROS DE ENTRADA (Pydantic)                 │
│  Request (hereda de Pagination):                                │
│  - skip, limit: Paginación (heredado, solo si all_data=false)  │
│  - all_data: true = todos, false = paginado (heredado)         │
│  - filters: Array de filtros opcionales (heredado)              │
│    El desarrollador puede filtrar por CUALQUIER campo del       │
│    response (UserExternalItem):                                 │
│    * platform_id, user_id, language_id, currency_id (UUIDs)    │
│    * email, identification, first_name, last_name, phone        │
│    * user_state (boolean)                                        │
│    * token_expiration_minutes, refresh_token_exp_minutes (int) │
│    * user_created_date, user_updated_date (fechas)              │
│    * platform_created_date, platform_updated_date (fechas)      │
│    Todos los campos retornados son filtrables (16 campos)       │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│     3. EJECUTAR QUERY CON JOINs EN SQLALCHEMY                   │
│                                                                  │
│  SELECT:                                                         │
│    platform.id (platform_id),                                   │
│    user.id (user_id),                                           │
│    user.email, user.identification,                             │
│    user.first_name, user.last_name, user.phone,                 │
│    user.state (user_state),                                     │
│    user.created_date (user_created_date),                       │
│    user.updated_date (user_updated_date),                       │
│    platform.language_id, platform.currency_id,                  │
│    platform.token_expiration_minutes,                           │
│    platform.refresh_token_expiration_minutes,                   │
│    platform.created_date (platform_created_date),               │
│    platform.updated_date (platform_updated_date)                │
│                                                                  │
│  FROM user                                                       │
│  INNER JOIN platform ON user.platform_id = platform.id         │
│  LEFT JOIN user_location_rol ON user.id = user_location_rol.user_id │
│                                                                  │
│  WHERE user.state = true                                        │
│  AND platform.location_id IS NULL      ← FILTRO 1              │
│  AND user_location_rol.id IS NULL      ← FILTRO 2 (SEGURIDAD)  │
│                                                                  │
│  ORDER BY user.first_name, user.last_name                       │
│                                                                  │
│  ⚡ OPTIMIZACIÓN DE PAGINACIÓN:                                 │
│  • Si NO hay filtros Y all_data=false:                          │
│    → stmt.offset(skip).limit(limit)  [PAGINACIÓN EN SQL]       │
│  • Si HAY filtros O all_data=true:                              │
│    → Traer todos los registros       [FILTRAR Y PAGINAR MEMORIA]│
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│     4. MAPEAR RESULTADOS A MODELO DE RESPUESTA                  │
│  Para cada fila del resultado:                                  │
│    - Crear UserExternalItem con todos los campos               │
│      (platform_id, user_id, email, language_id, currency_id,   │
│       token_expiration_minutes, etc.)                           │
│                                                                  │
│  Nota: Password NUNCA se incluye                                │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│     5. APLICAR FILTROS EN MEMORIA (solo si existen)            │
│  Si HAY filtros:                                                │
│    - Construir alias_map con build_alias_map()                 │
│    - Aplicar apply_memory_filters()                             │
│    - Si all_data=false: Paginar en memoria [skip:skip+limit]   │
│                                                                  │
│  Si NO hay filtros:                                             │
│    → Ya está paginado en SQL (skip)                             │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│     6. RETORNAR LISTA PAGINADA                                  │
│  {                                                               │
│    message_type: "temporary",                                    │
│    notification_type: "success",                                 │
│    message: "Consulta realizada exitosamente",                  │
│    response: [                                                   │
│      {                                                           │
│        platform_id: "uuid",                                      │
│        user_id: "uuid",                                          │
│        email: "cliente@example.com",                             │
│        identification: "98765432",                               │
│        first_name: "Carlos",                                     │
│        last_name: "Ramírez",                                     │
│        phone: "+573009876543",                                   │
│        user_state: true,                                         │
│        user_created_date: "2024-03-20T15:45:00Z",                │
│        user_updated_date: "2024-03-20T15:45:00Z",                │
│        language_id: "550e8400-uuid",                             │
│        currency_id: "770e8400-uuid",                             │
│        token_expiration_minutes: 60,                             │
│        refresh_token_expiration_minutes: 1440,                   │
│        platform_created_date: "2024-03-20T15:45:00Z",            │
│        platform_updated_date: "2024-03-20T15:45:00Z"             │
│      },                                                          │
│      ...                                                         │
│    ]                                                             │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Componentes Involucrados

### Archivos a Crear

#### 1. Response Model
- `src/domain/models/business/auth/list_users_external/user_external_item.py`
- `src/domain/models/business/auth/list_users_external/__init__.py`

**Nota**: NO se crea Request Model porque se usa directamente `Pagination` del core (`src/core/models/filter.py`)

#### 2. Mapper
- `src/infrastructure/database/repositories/business/mappers/auth/users_external/users_external_mapper.py`
- `src/infrastructure/database/repositories/business/mappers/auth/users_external/__init__.py`
- Función: `map_to_user_external_item(row)`

#### 3. Repository Method
- `src/infrastructure/database/repositories/business/auth_repository.py` (actualizar existente)
- Método: `users_external(config: Config, params: Pagination)`

#### 4. Use Case
- `src/domain/services/use_cases/business/auth/users_external/users_external_use_case.py`
- `src/domain/services/use_cases/business/auth/users_external/__init__.py`

#### 5. Controller Method
- `src/infrastructure/web/controller/business/auth_controller.py` (actualizar)
- Método: `users_external(config: Config, params: Pagination)`

#### 6. Router Endpoint
- `src/infrastructure/web/business_routes/auth_router.py` (actualizar)
- Endpoint: `POST /auth/users-external`
- Método: `users_external(params: Pagination, config: Config)`

---

## Endpoints API

### Endpoint: List Users External

```
POST /auth/users-external
```

**Descripción**: Lista usuarios externos (clientes) registrados en el sistema.

**Headers Requeridos:**
```
Content-Type: application/json
Authorization: Bearer {token}
Language: es | en
```

**Restricciones de Acceso:**
- **Autenticación**: Requiere token JWT válido
- **Permiso**: `PERMISSION_TYPE.READ`

**Request Body:**

```json
{
  "skip": 0,
  "limit": 10,
  "all_data": false,
  "filters": [
    {
      "field": "email",
      "condition": "like",
      "value": "@gmail.com"
    },
    {
      "field": "first_name",
      "condition": "like",
      "value": "Carlos"
    }
  ]
}
```

**Parámetros:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `skip` | int | No | Registros a saltar (heredado de `Pagination`, default: None). Solo aplica si `all_data=false` |
| `limit` | int | No | Registros a retornar (heredado de `Pagination`, default: None). Solo aplica si `all_data=false` |
| `all_data` | bool | No | Si es `true`, retorna TODOS los registros sin paginación. Si es `false`, aplica paginación (heredado de `Pagination`, default: false) |
| `filters` | array | No | Filtros opcionales (heredado de `Pagination`). **El desarrollador puede filtrar por CUALQUIER campo que está en el response** (`UserExternalItem`). |

**Filtros Disponibles:**

El desarrollador puede filtrar por **CUALQUIER campo que está en el response** del servicio (`UserExternalItem`):

| Campo del Response | Tipo | Operadores Sugeridos | Descripción |
|-------------------|------|---------------------|-------------|
| `platform_id` | UUID | equals, in | ID del platform |
| `user_id` | UUID | equals, in | ID del usuario |
| `email` | string | like, equals | Email del usuario |
| `identification` | string | equals, like | Documento de identificación |
| `first_name` | string | like, equals | Primer nombre |
| `last_name` | string | like, equals | Apellido |
| `phone` | string | like, equals | Teléfono |
| `user_state` | boolean | equals | Estado activo/inactivo del usuario |
| `user_created_date` | datetime | equals, gt, gte, lt, lte | Fecha de creación del usuario |
| `user_updated_date` | datetime | equals, gt, gte, lt, lte | Fecha de actualización del usuario |
| `language_id` | UUID | equals, in | ID del idioma |
| `currency_id` | UUID | equals, in | ID de la moneda |
| `token_expiration_minutes` | int | equals, gt, gte, lt, lte | Minutos de expiración del token |
| `refresh_token_expiration_minutes` | int | equals, gt, gte, lt, lte | Minutos de expiración del refresh token |
| `platform_created_date` | datetime | equals, gt, gte, lt, lte | Fecha de creación del platform |
| `platform_updated_date` | datetime | equals, gt, gte, lt, lte | Fecha de actualización del platform |

**Regla**: Si un campo existe en el response, puede ser usado como filtro.

**Operadores disponibles** (`apply_memory_filters` soporta):
- `equals`: Igualdad exacta
- `like`: Búsqueda con comodines (ej: "%carlos%")
- `in`: El valor está en una lista
- `not_in`: El valor NO está en una lista
- `gt`: Mayor que (>)
- `gte`: Mayor o igual (>=)
- `lt`: Menor que (<)
- `lte`: Menor o igual (<=)
- `is_null`: El valor es null
- `is_not_null`: El valor no es null

**Response (Success - 200 OK):**

```json
{
  "message_type": "temporary",
  "notification_type": "success",
  "message": "Consulta realizada exitosamente",
  "response": [
    {
      "platform_id": "ff0e8400-e29b-41d4-a716-446655440000",
      "user_id": "bb0e8400-e29b-41d4-a716-446655440000",
      "email": "carlos.ramirez@gmail.com",
      "identification": "98765432",
      "first_name": "Carlos",
      "last_name": "Ramírez",
      "phone": "+573009876543",
      "user_state": true,
      "user_created_date": "2024-03-20T15:45:00Z",
      "user_updated_date": "2024-03-20T15:45:00Z",
      "language_id": "550e8400-e29b-41d4-a716-446655440000",
      "currency_id": "770e8400-e29b-41d4-a716-446655440000",
      "token_expiration_minutes": 60,
      "refresh_token_expiration_minutes": 1440,
      "platform_created_date": "2024-03-20T15:45:00Z",
      "platform_updated_date": "2024-03-20T15:45:00Z"
    },
    {
      "platform_id": "gg0e8400-e29b-41d4-a716-446655440000",
      "user_id": "ee0e8400-e29b-41d4-a716-446655440000",
      "email": "ana.torres@hotmail.com",
      "identification": "11223344",
      "first_name": "Ana",
      "last_name": "Torres",
      "phone": "+573001122334",
      "user_state": true,
      "user_created_date": "2024-04-10T09:30:00Z",
      "user_updated_date": "2024-04-10T09:30:00Z",
      "language_id": "550e8400-e29b-41d4-a716-446655440000",
      "currency_id": "770e8400-e29b-41d4-a716-446655440000",
      "token_expiration_minutes": 60,
      "refresh_token_expiration_minutes": 1440,
      "platform_created_date": "2024-04-10T09:30:00Z",
      "platform_updated_date": "2024-04-10T09:30:00Z"
    }
  ]
}
```

**Response (Success - Sin Resultados):**

```json
{
  "message_type": "temporary",
  "notification_type": "success",
  "message": "No se encontraron resultados",
  "response": []
}
```

**Response (Error - Sin Autenticación):**

```json
{
  "detail": "Not authenticated"
}
```

**Response (Error - Sin Permisos):**

```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "No tienes permisos suficientes para realizar esta acción",
  "response": null
}
```

---

## Modelos de Datos

### Request Model

**No se requiere modelo personalizado**. Se usa directamente la clase `Pagination` del core:

**Archivo**: `src/core/models/filter.py` (ya existe)

```python
from typing import Any, List, Optional
from pydantic import BaseModel, Field
from src.core.enums.condition_type import CONDITION_TYPE


class FilterManager(BaseModel):
    field: str = Field(...)
    condition: CONDITION_TYPE = Field(...)
    value: Any = Field(...)
    group: Optional[int] = Field(None)


class Pagination(BaseModel):
    skip: Optional[int] = Field(default=None)
    limit: Optional[int] = Field(default=None)
    all_data: Optional[bool] = Field(default=False)
    filters: Optional[List[FilterManager]] = Field(default=None)
```

**Nota**: Se reutiliza directamente la clase `Pagination` existente.

### Response Model

**Archivo**: `src/domain/models/business/auth/list_users_external/user_external_item.py`

```python
from pydantic import BaseModel, Field, UUID4, EmailStr
from typing import Optional
from datetime import datetime


class UserExternalItem(BaseModel):
    platform_id: UUID4 = Field(..., description="ID del platform")
    user_id: UUID4 = Field(..., description="ID del usuario")
    email: EmailStr = Field(..., description="Email del usuario")
    identification: str = Field(..., description="Documento de identificación")
    first_name: str = Field(..., description="Primer nombre")
    last_name: str = Field(..., description="Apellido")
    phone: Optional[str] = Field(None, description="Teléfono")
    user_state: bool = Field(..., description="Estado del usuario (activo/inactivo)")
    user_created_date: datetime = Field(..., description="Fecha de creación del usuario")
    user_updated_date: datetime = Field(..., description="Fecha de última actualización del usuario")
    language_id: UUID4 = Field(..., description="ID del idioma")
    currency_id: UUID4 = Field(..., description="ID de la moneda")
    token_expiration_minutes: int = Field(..., description="Minutos de expiración del token")
    refresh_token_expiration_minutes: int = Field(..., description="Minutos de expiración del refresh token")
    platform_created_date: datetime = Field(..., description="Fecha de creación del platform")
    platform_updated_date: datetime = Field(..., description="Fecha de última actualización del platform")

    class Config:
        json_schema_extra = {
            "example": {
                "platform_id": "ff0e8400-e29b-41d4-a716-446655440000",
                "user_id": "bb0e8400-e29b-41d4-a716-446655440000",
                "email": "carlos.ramirez@gmail.com",
                "identification": "98765432",
                "first_name": "Carlos",
                "last_name": "Ramírez",
                "phone": "+573009876543",
                "user_state": True,
                "user_created_date": "2024-03-20T15:45:00Z",
                "user_updated_date": "2024-03-20T15:45:00Z",
                "language_id": "550e8400-e29b-41d4-a716-446655440000",
                "currency_id": "770e8400-e29b-41d4-a716-446655440000",
                "token_expiration_minutes": 60,
                "refresh_token_expiration_minutes": 1440,
                "platform_created_date": "2024-03-20T15:45:00Z",
                "platform_updated_date": "2024-03-20T15:45:00Z"
            }
        }
```

### Index Files

**Archivo**: `src/domain/models/business/auth/list_users_external/__init__.py`

```python
from .user_external_item import UserExternalItem

__all__ = [
    "UserExternalItem"
]
```

---

## Implementación con SQLAlchemy

### Mapper

**Archivo**: `src/infrastructure/database/repositories/business/mappers/auth/users_external/users_external_mapper.py`

```python
from src.domain.models.business.auth.list_users_external import (
    UserExternalItem
)


def map_to_user_external_item(row) -> UserExternalItem:
    return UserExternalItem(
        platform_id=row.platform_id,
        user_id=row.user_id,
        email=row.email,
        identification=row.identification,
        first_name=row.first_name,
        last_name=row.last_name,
        phone=row.phone,
        user_state=row.user_state,
        user_created_date=row.user_created_date,
        user_updated_date=row.user_updated_date,
        language_id=row.language_id,
        currency_id=row.currency_id,
        token_expiration_minutes=row.token_expiration_minutes,
        refresh_token_expiration_minutes=row.refresh_token_expiration_minutes,
        platform_created_date=row.platform_created_date,
        platform_updated_date=row.platform_updated_date,
    )
```

**Archivo**: `src/infrastructure/database/repositories/business/mappers/auth/users_external/__init__.py`

```python
from .users_external_mapper import map_to_user_external_item

__all__ = ["map_to_user_external_item"]
```

---

### Repository Method

**Archivo**: `src/infrastructure/database/repositories/business/auth_repository.py` (Actualizar existente)

Agregar nuevo método:

```python
from typing import List, Union
from sqlalchemy.future import select
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.wrappers.execute_transaction import execute_transaction
from src.core.methods.apply_memory_filters import apply_memory_filters
from src.core.methods.build_alias_map import build_alias_map

from src.domain.models.business.auth.list_users_external import (
    UserExternalItem
)

from src.infrastructure.database.entities.user_entity import UserEntity
from src.infrastructure.database.entities.platform_entity import PlatformEntity
from src.infrastructure.database.entities.user_location_rol_entity import (
    UserLocationRolEntity
)

from src.infrastructure.database.repositories.business.mappers.auth.users_external import (
    map_to_user_external_item
)


class AuthRepository:
    
    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def users_external(
        self,
        config: Config,
        params: Pagination
    ) -> Union[List[UserExternalItem], None]:
        async with config.async_db as db:
            stmt = (
                select(
                    PlatformEntity.id.label("platform_id"),
                    UserEntity.id.label("user_id"),
                    UserEntity.email,
                    UserEntity.identification,
                    UserEntity.first_name,
                    UserEntity.last_name,
                    UserEntity.phone,
                    UserEntity.state.label("user_state"),
                    UserEntity.created_date.label("user_created_date"),
                    UserEntity.updated_date.label("user_updated_date"),
                    PlatformEntity.language_id,
                    PlatformEntity.currency_id,
                    PlatformEntity.token_expiration_minutes,
                    PlatformEntity.refresh_token_expiration_minutes,
                    PlatformEntity.created_date.label("platform_created_date"),
                    PlatformEntity.updated_date.label("platform_updated_date"),
                )
                .join(PlatformEntity, UserEntity.platform_id == PlatformEntity.id)
                .outerjoin(UserLocationRolEntity, UserEntity.id == UserLocationRolEntity.user_id)
                .filter(UserEntity.state == True)
                .filter(PlatformEntity.location_id.is_(None))
                .filter(UserLocationRolEntity.id.is_(None))
                .order_by(UserEntity.first_name, UserEntity.last_name)
            )
            
            if not params.filters and not params.all_data:
                stmt = stmt.offset(params.skip).limit(params.limit)
            
            result = await db.execute(stmt)
            results = result.all()
            
            if not results:
                return None
            
            users_external: List[UserExternalItem] = [
                map_to_user_external_item(row)
                for row in results
            ]
            
            if params.filters:
                alias_map = build_alias_map(response_class=UserExternalItem)
                
                users_external = [
                    user
                    for user in users_external
                    if apply_memory_filters(user, params.filters, alias_map)
                ]
                
                if not params.all_data:
                    skip = params.skip if params.skip is not None else 0
                    limit = params.limit if params.limit is not None else 10
                    users_external = users_external[skip : skip + limit]
            
            return users_external
```

**Imports necesarios** (agregar al inicio del archivo):

```python
from src.domain.models.business.auth.list_users_external import UserExternalItem
from src.infrastructure.database.repositories.business.mappers.auth.users_external import (
    map_to_user_external_item
)
from src.infrastructure.database.entities.platform_entity import PlatformEntity
from src.infrastructure.database.entities.user_location_rol_entity import (
    UserLocationRolEntity
)
```

**Nota Importante**: Este método hace **LEFT JOIN** (outerjoin) con `user_location_rol` para validar que **NO existe** ningún registro para el usuario. Esto garantiza que realmente es un usuario externo que no tiene roles ni ubicaciones asignadas.

---

### Use Case

**Archivo**: `src/domain/services/use_cases/business/auth/users_external/users_external_use_case.py`

```python
from typing import List, Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.wrappers.execute_transaction import execute_transaction

from src.domain.models.business.auth.list_users_external import (
    UserExternalItem
)

from src.infrastructure.database.repositories.business.auth_repository import (
    AuthRepository
)


auth_repository = AuthRepository()


class UsersExternalUseCase:
    def __init__(self):
        self.auth_repository = auth_repository

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[UserExternalItem], None]:
        config.response_type = RESPONSE_TYPE.OBJECT
        
        users = await self.auth_repository.users_external(
            config=config,
            params=params
        )
        
        return users
```

**Archivo**: `src/domain/services/use_cases/business/auth/users_external/__init__.py`

```python
from .users_external_use_case import UsersExternalUseCase

__all__ = ["UsersExternalUseCase"]
```

---

### Controller

**Archivo**: `src/infrastructure/web/controller/business/auth_controller.py` (Actualizar)

Agregar import:

```python
from src.domain.models.business.auth.list_users_external import (
    UserExternalItem
)
from src.domain.services.use_cases.business.auth.users_external import (
    UsersExternalUseCase,
)
```

En el `__init__`:

```python
self.users_external_use_case = UsersExternalUseCase()
```

Agregar método:

```python
@execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
async def users_external(
    self, 
    config: Config, 
    params: Pagination
) -> Response[List[UserExternalItem]]:
    result = await self.users_external_use_case.execute(
        config=config, 
        params=params
    )
    
    if not result:
        return Response.success_temporary_message(
            response=[],
            message=await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_NO_RESULTS_FOUND.value
                ),
            ),
        )
    
    return Response.success_temporary_message(
        response=result,
        message=await self.message.get_message(
            config=config,
            message=MessageCoreEntity(
                key=KEYS_MESSAGES.CORE_QUERY_MADE.value
            ),
        ),
    )
```

---

### Router

**Archivo**: `src/infrastructure/web/business_routes/auth_router.py` (Actualizar)

Agregar import:

```python
from src.domain.models.business.auth.list_users_external import (
    UserExternalItem
)
```

Agregar endpoint:

```python
@auth_router.post(
    "/users-external",
    status_code=status.HTTP_200_OK,
    response_model=Response[List[UserExternalItem]]
)
@check_permissions([PERMISSION_TYPE.READ.value])
@execute_transaction_route(enabled=settings.has_track)
async def users_external(
    params: Pagination,
    config: Config = Depends(get_config)
) -> Response[List[UserExternalItem]]:
    return await auth_controller.users_external(config=config, params=params)
```

---

## Paginación y Filtros

### Paginación

**Parámetros:**
- `skip`: Registros a saltar (default: None)
- `limit`: Registros a retornar (default: None)
- `all_data`: Boolean para retornar todos los registros sin paginar (default: False)

**⚡ Optimización de Paginación (Dual Strategy):**

El sistema utiliza una estrategia **dual** para optimizar el rendimiento:

**Caso 1 - Paginación en SQL (Más Eficiente):**
- **Condición**: NO hay filtros Y `all_data=false`
- **Acción**: Aplica `stmt.offset(skip).limit(limit)` en SQLAlchemy
- **Ventaja**: Solo trae de BD los registros necesarios
- **Ejemplo**: Request sin `filters` → Paginación en SQL

**Caso 2 - Paginación en Memoria:**
- **Condición**: HAY filtros O `all_data=true`
- **Acción**: Trae todos los registros, filtra en memoria, luego pagina en memoria
- **Razón**: Los filtros se aplican en memoria, por lo que necesitamos todos los registros primero
- **Ejemplo**: Request con `filters` → Filtrar primero, paginar después

**Comportamiento:**
- **Si `all_data = false`** (default): Aplica paginación (SQL o memoria según filtros)
- **Si `all_data = true`**: Retorna TODOS los registros sin paginar

**Flexibilidad Total:** El desarrollador puede filtrar por **cualquier campo que está en el response**. Si el campo se retorna en `UserExternalItem`, entonces es filtrable.

**Ejemplo 1 - Buscar clientes por email (paginado):**
```json
{
  "skip": 0,
  "limit": 10,
  "all_data": false,
  "filters": [
    {
      "field": "email",
      "condition": "like",
      "value": "@gmail.com"
    }
  ]
}
```
Retorna registros 1-10 de usuarios con email de Gmail.

**Ejemplo 2 - Todos los usuarios externos activos:**
```json
{
  "all_data": true,
  "filters": [
    {
      "field": "user_state",
      "condition": "equals",
      "value": true
    }
  ]
}
```
Retorna TODOS los usuarios externos activos.

**Ejemplo 3 - Buscar por nombre y apellido:**
```json
{
  "skip": 0,
  "limit": 20,
  "filters": [
    {
      "field": "first_name",
      "condition": "like",
      "value": "Carlos"
    },
    {
      "field": "last_name",
      "condition": "like",
      "value": "Ramírez"
    }
  ]
}
```

### Ejemplos de Filtros por Tipo de Campo

**Filtros por UUIDs:**
```json
{"field": "user_id", "condition": "equals", "value": "uuid"}
{"field": "platform_id", "condition": "in", "value": ["uuid1", "uuid2"]}
{"field": "language_id", "condition": "equals", "value": "uuid"}
```

**Filtros por Strings:**
```json
{"field": "email", "condition": "like", "value": "@gmail.com"}
{"field": "first_name", "condition": "like", "value": "Carlos"}
{"field": "identification", "condition": "equals", "value": "98765432"}
```

**Filtros por Boolean:**
```json
{"field": "user_state", "condition": "equals", "value": true}
```

**Filtros por Fechas:**
```json
{"field": "user_created_date", "condition": "gte", "value": "2024-01-01T00:00:00Z"}
{"field": "platform_updated_date", "condition": "lt", "value": "2024-12-31T23:59:59Z"}
```

**Filtros por Números:**
```json
{"field": "token_expiration_minutes", "condition": "gte", "value": 60}
{"field": "refresh_token_expiration_minutes", "condition": "lte", "value": 1440}
```

---

## Manejo de Errores

| Error | Código HTTP | Descripción |
|-------|-------------|-------------|
| Sin autenticación | 401 | Token JWT no proporcionado o inválido |
| Sin permisos | 403 | Usuario no tiene permiso READ |
| Sin resultados | 200 | Retorna array vacío con mensaje |
| Error en BD | 500 | Error interno del servidor |

---

## Seguridad

### Autenticación y Autorización
- ✅ **Token JWT**: Obligatorio
- ✅ **Permiso**: `PERMISSION_TYPE.READ`
- ✅ **Password**: Nunca se expone en la respuesta

### Protección de Datos
- ✅ **Password excluido**: El campo password de user NO se incluye
- ✅ **SQL Injection**: Protección por SQLAlchemy ORM
- ✅ **Rate Limiting**: Aplicable según configuración

### Filtros de Seguridad Críticos

**Doble Validación SQL Obligatoria - Solo Usuarios Externos:**

**Filtro 1 - Platform sin ubicación:**
```python
.filter(PlatformEntity.location_id.is_(None))
```
- **Propósito**: Primera validación - usuarios externos tienen `platform.location_id = NULL`
- **Nivel**: Capa de base de datos

**Filtro 2 - Sin registro en user_location_rol:**
```python
.outerjoin(UserLocationRolEntity, UserEntity.id == UserLocationRolEntity.user_id)
.filter(UserLocationRolEntity.id.is_(None))
```
- **Propósito**: Segunda validación - usuarios externos **NO tienen** registros en `user_location_rol`
- **Técnica**: LEFT JOIN para encontrar usuarios sin registros en `user_location_rol`
- **Nivel**: Capa de base de datos

**Justificación de Seguridad:**
- **Doble capa de protección** para garantizar que solo se retornan usuarios externos
- El filtro 1 (`platform.location_id IS NULL`) es el identificador principal
- El filtro 2 (`user_location_rol.id IS NULL`) valida que no existan roles/ubicaciones asignados
- Esta doble validación previene casos edge donde:
  - Un usuario podría tener `platform.location_id = NULL` pero tener registros en `user_location_rol`
  - Garantiza separación absoluta entre usuarios internos (empleados) y externos (clientes)
- Imposible mezclar usuarios internos con externos por error o manipulación

---

## Ejemplos de Uso

### Caso 1: Listar todos los usuarios externos (paginado)

**Request:**
```bash
curl -X POST https://api.goluti.com/auth/users-external \
  -H "Authorization: Bearer TOKEN" \
  -H "Language: es" \
  -H "Content-Type: application/json" \
  -d '{
    "skip": 0,
    "limit": 10
  }'
```

**Response:**
```json
{
  "message_type": "temporary",
  "notification_type": "success",
  "message": "Consulta realizada exitosamente",
  "response": [
    {
      "platform_id": "ff0e8400",
      "user_id": "bb0e8400",
      "email": "carlos@gmail.com",
      "identification": "98765432",
      "first_name": "Carlos",
      "last_name": "Ramírez",
      "phone": "+573009876543",
      "user_state": true,
      "user_created_date": "2024-03-20T15:45:00Z",
      "user_updated_date": "2024-03-20T15:45:00Z",
      "language_id": "550e8400",
      "currency_id": "770e8400",
      "token_expiration_minutes": 60,
      "refresh_token_expiration_minutes": 1440,
      "platform_created_date": "2024-03-20T15:45:00Z",
      "platform_updated_date": "2024-03-20T15:45:00Z"
    }
  ]
}
```

### Caso 2: Buscar clientes por email

**Request:**
```bash
curl -X POST https://api.goluti.com/auth/users-external \
  -H "Authorization: Bearer TOKEN" \
  -H "Language: es" \
  -H "Content-Type: application/json" \
  -d '{
    "skip": 0,
    "limit": 10,
    "filters": [
      {
        "field": "email",
        "condition": "like",
        "value": "@gmail.com"
      }
    ]
  }'
```

### Caso 3: Buscar por identificación específica

**Request:**
```bash
curl -X POST https://api.goluti.com/auth/users-external \
  -H "Authorization: Bearer TOKEN" \
  -H "Language: es" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [
      {
        "field": "identification",
        "condition": "equals",
        "value": "98765432"
      }
    ]
  }'
```

### Caso 4: Filtrar por configuración de token

**Request:**
```bash
curl -X POST https://api.goluti.com/auth/users-external \
  -H "Authorization: Bearer TOKEN" \
  -H "Language: es" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [
      {
        "field": "token_expiration_minutes",
        "condition": "gte",
        "value": 60
      }
    ]
  }'
```

---

## Testing

### Tests Unitarios

**Archivo**: `tests/domain/services/use_cases/business/auth/users_external/test_users_external_use_case.py`

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.core.models.filter import Pagination, FilterManager
from src.core.enums.condition_type import CONDITION_TYPE
from src.domain.services.use_cases.business.auth.users_external import (
    UsersExternalUseCase
)

@pytest.mark.asyncio
async def test_users_external_success():
    use_case = UsersExternalUseCase()
    config = MagicMock()
    
    request = Pagination(
        skip=0,
        limit=10,
        filters=[
            FilterManager(
                field="email", 
                condition=CONDITION_TYPE.LIKE, 
                value="@gmail.com"
            )
        ]
    )
    
    result = await use_case.execute(config=config, params=request)
    
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_users_external_by_language():
    use_case = UsersExternalUseCase()
    config = MagicMock()
    
    request = Pagination(
        skip=0,
        limit=10,
        filters=[
            FilterManager(
                field="language_id", 
                condition=CONDITION_TYPE.EQUALS, 
                value="550e8400-e29b-41d4-a716-446655440000"
            )
        ]
    )
    
    result = await use_case.execute(config=config, params=request)
    
    assert isinstance(result, list)
```

### Tests de Integración

**Archivo**: `tests/infrastructure/web/business_routes/test_auth_router.py`

```python
@pytest.mark.asyncio
async def test_users_external_endpoint(client: AsyncClient, admin_token):
    response = await client.post(
        "/auth/users-external",
        headers={"Authorization": f"Bearer {admin_token}", "Language": "es"},
        json={
            "skip": 0,
            "limit": 10,
            "filters": [
                {
                    "field": "email",
                    "condition": "like",
                    "value": "@gmail.com"
                }
            ]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["notification_type"] == "success"
    assert isinstance(data["response"], list)


@pytest.mark.asyncio
async def test_users_external_by_platform_field(client: AsyncClient, admin_token):
    response = await client.post(
        "/auth/users-external",
        headers={"Authorization": f"Bearer {admin_token}", "Language": "es"},
        json={
            "skip": 0,
            "limit": 10,
            "filters": [
                {
                    "field": "token_expiration_minutes",
                    "condition": "equals",
                    "value": 60
                }
            ]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["response"], list)
```

---

## Consideraciones Técnicas

### Performance
- ✅ **Consulta Optimizada**: Query con JOIN entre `user` y `platform`, LEFT JOIN con `user_location_rol`
- ✅ **Filtros en Memoria**: Usando helpers del core (`apply_memory_filters`, `build_alias_map`)
- ✅ **Paginación Dual**: SQL cuando no hay filtros, memoria cuando hay filtros
- ✅ **Índices Requeridos**:
  - `platform.location_id` (para filtro de usuarios externos)
  - `user_location_rol.user_id` (para LEFT JOIN eficiente)
  - `user.platform_id` (para JOIN principal)
  - `user.email` y `user.identification` (para búsquedas frecuentes)

### Escalabilidad
- ✅ **Limit máximo**: 100 registros por página recomendado
- ✅ **Query eficiente**: Sin N+1 queries, 1 INNER JOIN + 1 LEFT JOIN
- ✅ **Filtros en memoria**: Usando `apply_memory_filters` y `build_alias_map` (patrón del proyecto)
- ✅ **Validación robusta**: Doble filtro en SQL garantiza solo usuarios externos

### Mejoras Futuras
1. **Cache**: Cachear resultados frecuentes
2. **Filtros avanzados**: OR lógico, rangos de fechas
3. **Ordenamiento**: Permitir ordenar por diferentes campos
4. **Exportación**: Generar CSV/Excel de clientes
5. **Estadísticas**: Total de usuarios externos registrados por idioma/moneda
6. **Búsqueda Full-Text**: Búsqueda avanzada en múltiples campos
7. **Agregaciones**: Conteos por idioma, moneda, estado

---

## Historial de Cambios

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 2.2 | Nov 11, 2024 | **Corrección crítica**: Removido campo `platform_state` que no existe en `PlatformEntity`. **Response Model corregido**: `UserExternalItem` incluye **16 campos** (user + platform): `platform_id`, `user_id`, `email`, `identification`, `first_name`, `last_name`, `phone`, `user_state`, `user_created_date`, `user_updated_date`, `language_id`, `currency_id`, `token_expiration_minutes`, `refresh_token_expiration_minutes`, `platform_created_date`, `platform_updated_date`. Actualizado query, mapper, y ejemplos para reflejar el cambio. | Equipo de Desarrollo Goluti |
| 2.1 | Nov 11, 2024 | **Mejora de seguridad crítica**: Agregada **doble validación** para usuarios externos. **Query actualizado** con LEFT JOIN a `user_location_rol` para validar que **NO existe** ningún registro. **Filtros de seguridad**: 1) `platform.location_id IS NULL` (identificador principal), 2) `user_location_rol.id IS NULL` (validación adicional mediante LEFT JOIN). Esta doble capa de protección previene casos edge y garantiza separación absoluta entre usuarios internos y externos. Actualizada sección de seguridad, índices requeridos, y consideraciones técnicas para reflejar el query con 1 INNER JOIN + 1 LEFT JOIN. | Equipo de Desarrollo Goluti |
| 2.0 | Nov 11, 2024 | **Reescritura completa** de la especificación. **Cambio fundamental**: Los usuarios externos **NO tienen registro en `user_location_rol` ni `rol`**. Se registran **SOLO** en las tablas `user` y `platform`. **Query corregido**: JOIN únicamente entre `user` y `platform`. **Filtro correcto**: `platform.location_id IS NULL` (identificador de usuarios externos). **Response Model actualizado**: `UserExternalItem` incluye campos de `user` + `platform` (17 campos totales - luego corregido a 16). Sin campos de `rol` ni `location_id`. Filtros aplicables a CUALQUIER campo del response. Paginación dual (SQL/memoria). | Equipo de Desarrollo Goluti |
| 1.0 | Nov 11, 2024 | ~~Versión inicial incorrecta~~ (obsoleta) | Equipo de Desarrollo Goluti |

---

**Fin del Documento**

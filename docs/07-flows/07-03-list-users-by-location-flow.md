# Especificación de Flujo: List Users by Location

**Documento:** 07-03-list-users-by-location-flow.md  
**Versión:** 1.1  
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

Este documento especifica el flujo de negocio para **listar usuarios internos por ubicación** en el sistema Goluti Backend Platform. El servicio permite consultar todos los usuarios que están asignados a una ubicación específica, obteniendo información completa del usuario (excepto password) y sus roles asignados.

**Características principales:**
- ✅ Consulta paginada de usuarios por ubicación
- ✅ Uso directo de SQLAlchemy con JOINs entre tablas
- ✅ Retorna información de User + Rol sin el password
- ✅ Soporte de filtros avanzados (nombre, email, identification, rol, etc.)
- ✅ Un usuario interno tiene UN SOLO rol por ubicación
- ✅ Requiere autenticación y permisos de lectura

---

## Objetivo del Flujo

Permitir consultar de manera eficiente todos los usuarios internos (empleados, colaboradores) que están asignados a una ubicación específica, mostrando sus roles y datos personales (excepto información sensible como el password).

### Alcance

**En alcance:**
- ✅ Sistema de filtros **flexible y genérico** usando `filters`
- ✅ **El desarrollador puede filtrar por CUALQUIER campo del response** (`UserByLocationItem`)
- ✅ Todos los campos retornados son filtrables: IDs, strings, booleans, fechas
- ✅ JOIN entre `user_location_rol`, `user` y `rol`
- ✅ Paginación configurable con `all_data` flag:
  - `all_data=false`: Aplica paginación (skip/limit)
  - `all_data=true`: Retorna todos los registros
- ✅ Filtros aplicados en memoria usando `apply_memory_filters` y `build_alias_map`
- ✅ Retornar información completa del usuario (sin password)
- ✅ Retornar información del rol asignado
- ✅ Un usuario interno tiene UN SOLO rol por ubicación (constraint único)
- ✅ Requiere autenticación y permiso READ

**Fuera de alcance:**
- ❌ Usuarios externos (sin roles/ubicaciones)
- ❌ Información de otras ubicaciones
- ❌ Modificación de datos (solo lectura)
- ❌ Información del password (nunca se expone)
- ❌ Historial de cambios de roles
- ❌ Múltiples roles para un usuario en la MISMA ubicación (restricción de negocio)

---

## Contexto de Negocio

### Problema

Los administradores y gerentes necesitan visualizar qué usuarios internos están asignados a una ubicación específica, junto con su rol único, para:
- Gestionar equipos por sucursal/sede
- Asignar tareas a empleados de una ubicación
- Verificar quién tiene qué rol en cada ubicación
- Auditar asignaciones de personal

**Regla de Negocio**: Un usuario interno tiene **UN SOLO rol por ubicación**. La combinación `(user_id, location_id)` es única en la tabla `user_location_rol`.

### Solución

Crear un endpoint `/auth/users-internal` que:
1. Usa sistema de filtros genérico y flexible
2. **El desarrollador puede filtrar por CUALQUIER campo del response**
3. Todos los campos retornados son automáticamente filtrables
4. Hace JOIN entre `user_location_rol`, `user` y `rol`
5. Retorna lista paginada con información de usuarios y roles
6. Excluye el password del usuario
7. Filtros aplicados en memoria usando `apply_memory_filters` y `build_alias_map`

### Beneficios

- ✅ **Performance**: Query optimizado con JOIN directo
- ✅ **Seguridad**: Password nunca se expone
- ✅ **Flexibilidad Total**: Cualquier campo del response es filtrable automáticamente
- ✅ **Escalabilidad**: Paginación para grandes volúmenes
- ✅ **Completitud**: Información de user + rol en una sola consulta
- ✅ **Consistencia**: Un usuario = Un rol por ubicación (constraint único)

---

## Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────────┐
│             INICIO: List Users by Location                      │
│           POST /auth/users-internal                              │
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
│    response (UserByLocationItem):                               │
│    * user_location_rol_id, location_id, user_id (UUIDs)         │
│    * email, identification, first_name, last_name, phone        │
│    * user_state (boolean)                                       │
│    * user_created_date, user_updated_date (fechas)              │
│    * rol_id, rol_name, rol_code, rol_description               │
│    Todos los campos retornados son filtrables                   │
│    location_id se filtra opcionalmente mediante filters         │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│     3. EJECUTAR QUERY CON JOINS EN SQLALCHEMY                   │
│                                                                  │
│  SELECT:                                                         │
│    user_location_rol.id, user_location_rol.location_id,         │
│    user.id, user.email, user.identification,                    │
│    user.first_name, user.last_name, user.phone,                 │
│    user.state, user.created_date, user.updated_date,            │
│    rol.id, rol.name, rol.code, rol.description                  │
│                                                                  │
│  FROM user_location_rol                                         │
│  INNER JOIN user ON user_location_rol.user_id = user.id        │
│  INNER JOIN rol ON user_location_rol.rol_id = rol.id           │
│                                                                  │
│  WHERE user_location_rol.state = true                           │
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
│    - Crear UserByLocationItem con todos los campos              │
│      (user_location_rol_id, location_id, user_id, email, etc.) │
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
│        user_location_rol_id: "uuid",                             │
│        user_id: "uuid",                                          │
│        email: "user@example.com",                                │
│        identification: "12345678",                               │
│        first_name: "Juan",                                       │
│        last_name: "Pérez",                                       │
│        phone: "+573001234567",                                   │
│        user_state: true,                                         │
│        rol_id: "uuid",                                           │
│        rol_name: "Administrador",                                │
│        rol_code: "ADMIN",                                        │
│        rol_description: "Administrador del sistema"              │
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
- `src/domain/models/business/auth/list_users_by_location/user_by_location_item.py`
- `src/domain/models/business/auth/list_users_by_location/__init__.py`

**Nota**: NO se crea Request Model porque se usa directamente `Pagination` del core (`src/core/models/filter.py`)

#### 2. Mapper
- `src/infrastructure/database/repositories/business/mappers/auth/users_internal/users_internal_mapper.py`
- `src/infrastructure/database/repositories/business/mappers/auth/users_internal/__init__.py`
- Función: `map_to_user_by_location_item(row)`

#### 3. Repository Method
- `src/infrastructure/database/repositories/business/auth_repository.py` (crear nuevo)
- Método: `users_internal(config: Config, params: Pagination)`

#### 4. Use Case
- `src/domain/services/use_cases/business/auth/users_internal/users_internal_use_case.py`
- `src/domain/services/use_cases/business/auth/users_internal/__init__.py`

#### 5. Controller Method
- `src/infrastructure/web/controller/business/auth_controller.py` (actualizar)
- Método: `users_internal(config: Config, params: Pagination)`

#### 6. Router Endpoint
- `src/infrastructure/web/business_routes/auth_router.py` (actualizar)
- Endpoint: `POST /auth/users-internal`
- Método: `users_internal(params: Pagination, config: Config)`

---

## Endpoints API

### Endpoint: List Users Internal

```
POST /auth/users-internal
```

**Descripción**: Lista usuarios internos asignados a una ubicación específica con información de sus roles.

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
      "field": "location_id",
      "condition": "equals",
      "value": "660e8400-e29b-41d4-a716-446655440000"
    },
    {
      "field": "first_name",
      "condition": "like",
      "value": "Juan"
    },
    {
      "field": "rol_id",
      "condition": "equals",
      "value": "880e8400-e29b-41d4-a716-446655440000"
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
| `filters` | array | No | Filtros opcionales (heredado de `Pagination`). **El desarrollador puede filtrar por CUALQUIER campo que está en el response** (`UserByLocationItem`): `user_location_rol_id`, `location_id`, `user_id`, `email`, `identification`, `first_name`, `last_name`, `phone`, `user_state`, `user_created_date`, `user_updated_date`, `rol_id`, `rol_name`, `rol_code`, `rol_description`. |

**Filtros Disponibles:**

El desarrollador puede filtrar por **CUALQUIER campo que está en el response** del servicio (`UserByLocationItem`):

| Campo del Response | Tipo | Operadores Sugeridos | Descripción |
|-------------------|------|---------------------|-------------|
| `user_location_rol_id` | UUID | equals, in | ID de la asignación user-location-rol |
| `location_id` | UUID | equals, in | Ubicación específica o múltiples ubicaciones |
| `user_id` | UUID | equals, in | ID del usuario |
| `email` | string | like, equals | Email del usuario |
| `identification` | string | equals, like | Documento de identificación |
| `first_name` | string | like, equals | Primer nombre |
| `last_name` | string | like, equals | Apellido |
| `phone` | string | like, equals | Teléfono |
| `user_state` | boolean | equals | Estado activo/inactivo |
| `user_created_date` | datetime | equals, gt, gte, lt, lte | Fecha de creación |
| `user_updated_date` | datetime | equals, gt, gte, lt, lte | Fecha de actualización |
| `rol_id` | UUID | equals, in | ID del rol |
| `rol_name` | string | like, equals | Nombre del rol |
| `rol_code` | string | equals, in | Código del rol (ADMIN, OPERATOR, etc.) |
| `rol_description` | string | like, equals | Descripción del rol |

**Regla**: Si un campo existe en el response, puede ser usado como filtro.

**Operadores disponibles** (`apply_memory_filters` soporta):
- `equals`: Igualdad exacta
- `like`: Búsqueda con comodines (ej: "%juan%")
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
      "user_location_rol_id": "aa0e8400-e29b-41d4-a716-446655440000",
      "location_id": "660e8400-e29b-41d4-a716-446655440000",
      "user_id": "bb0e8400-e29b-41d4-a716-446655440000",
      "email": "juan.perez@goluti.com",
      "identification": "12345678",
      "first_name": "Juan",
      "last_name": "Pérez",
      "phone": "+573001234567",
      "user_state": true,
      "user_created_date": "2024-01-15T10:30:00Z",
      "user_updated_date": "2024-01-15T10:30:00Z",
      "rol_id": "880e8400-e29b-41d4-a716-446655440000",
      "rol_name": "Administrador",
      "rol_code": "ADMIN",
      "rol_description": "Administrador del sistema"
    },
    {
      "user_location_rol_id": "dd0e8400-e29b-41d4-a716-446655440000",
      "location_id": "660e8400-e29b-41d4-a716-446655440000",
      "user_id": "ee0e8400-e29b-41d4-a716-446655440000",
      "email": "maria.lopez@goluti.com",
      "identification": "87654321",
      "first_name": "María",
      "last_name": "López",
      "phone": "+573007654321",
      "user_state": true,
      "user_created_date": "2024-02-10T14:20:00Z",
      "user_updated_date": "2024-02-10T14:20:00Z",
      "rol_id": "990e8400-e29b-41d4-a716-446655440000",
      "rol_name": "Operador",
      "rol_code": "OPERATOR",
      "rol_description": "Operador de sucursal"
    }
  ]
}
```

**Nota**: Cada usuario aparece **UNA SOLA VEZ** en los resultados de una ubicación específica, ya que solo puede tener un rol por ubicación. Si el mismo usuario tiene roles en DIFERENTES ubicaciones, aparecerá en diferentes consultas (filtrando por cada location_id).

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

**Nota**: Se reutiliza directamente la clase `Pagination` existente:
- `skip`: Optional[int] = None
- `limit`: Optional[int] = None
- `all_data`: Optional[bool] = False
- `filters`: Optional[List[FilterManager]] = None

**`location_id` es opcional**: Se filtra usando el campo `filters` si se necesita una ubicación específica.

### Response Model

**Archivo**: `src/domain/models/business/auth/list_users_by_location/user_by_location_item.py`

```python
from pydantic import BaseModel, Field, UUID4, EmailStr
from typing import Optional
from datetime import datetime


class UserByLocationItem(BaseModel):
    user_location_rol_id: UUID4 = Field(..., description="ID de la asignación user-location-rol")
    location_id: UUID4 = Field(..., description="ID de la ubicación")
    user_id: UUID4 = Field(..., description="ID del usuario")
    email: EmailStr = Field(..., description="Email del usuario")
    identification: str = Field(..., description="Documento de identificación")
    first_name: str = Field(..., description="Primer nombre")
    last_name: str = Field(..., description="Apellido")
    phone: Optional[str] = Field(None, description="Teléfono")
    user_state: bool = Field(..., description="Estado del usuario (activo/inactivo)")
    user_created_date: datetime = Field(..., description="Fecha de creación del usuario")
    user_updated_date: datetime = Field(..., description="Fecha de última actualización")
    rol_id: UUID4 = Field(..., description="ID del rol")
    rol_name: str = Field(..., description="Nombre del rol")
    rol_code: str = Field(..., description="Código del rol")
    rol_description: Optional[str] = Field(None, description="Descripción del rol")

    class Config:
        json_schema_extra = {
            "example": {
                "user_location_rol_id": "aa0e8400-e29b-41d4-a716-446655440000",
                "location_id": "660e8400-e29b-41d4-a716-446655440000",
                "user_id": "bb0e8400-e29b-41d4-a716-446655440000",
                "email": "juan.perez@goluti.com",
                "identification": "12345678",
                "first_name": "Juan",
                "last_name": "Pérez",
                "phone": "+573001234567",
                "user_state": True,
                "user_created_date": "2024-01-15T10:30:00Z",
                "user_updated_date": "2024-01-15T10:30:00Z",
                "rol_id": "880e8400-e29b-41d4-a716-446655440000",
                "rol_name": "Administrador",
                "rol_code": "ADMIN",
                "rol_description": "Administrador del sistema"
            }
        }
```

### Index Files

**Archivo**: `src/domain/models/business/auth/list_users_by_location/__init__.py`

```python
from .user_by_location_item import UserByLocationItem

__all__ = [
    "UserByLocationItem"
]
```

**Nota**: No se requiere `ListUsersByLocationRequest` porque se usa directamente `Pagination` del core.

---

## Implementación con SQLAlchemy

### Mapper

**Archivo**: `src/infrastructure/database/repositories/business/mappers/auth/users_internal/users_internal_mapper.py`

```python
from src.domain.models.business.auth.list_users_by_location import (
    UserByLocationItem
)


def map_to_user_by_location_item(row) -> UserByLocationItem:
    return UserByLocationItem(
        user_location_rol_id=row.user_location_rol_id,
        location_id=row.location_id,
        user_id=row.user_id,
        email=row.email,
        identification=row.identification,
        first_name=row.first_name,
        last_name=row.last_name,
        phone=row.phone,
        user_state=row.user_state,
        user_created_date=row.user_created_date,
        user_updated_date=row.user_updated_date,
        rol_id=row.rol_id,
        rol_name=row.rol_name,
        rol_code=row.rol_code,
        rol_description=row.rol_description,
    )
```

**Archivo**: `src/infrastructure/database/repositories/business/mappers/auth/users_internal/__init__.py`

```python
from .users_internal_mapper import map_to_user_by_location_item

__all__ = ["map_to_user_by_location_item"]
```

---

### Repository Method

**Archivo**: `src/infrastructure/database/repositories/business/auth_repository.py` (Nuevo)

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

from src.domain.models.business.auth.list_users_by_location import (
    UserByLocationItem
)

from src.infrastructure.database.entities.user_location_rol_entity import (
    UserLocationRolEntity
)
from src.infrastructure.database.entities.user_entity import UserEntity
from src.infrastructure.database.entities.rol_entity import RolEntity

from src.infrastructure.database.repositories.business.mappers.auth.users_internal import (
    map_to_user_by_location_item
)


class AuthRepository:
    
    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def users_internal(
        self,
        config: Config,
        params: Pagination
    ) -> Union[List[UserByLocationItem], None]:
        async with config.async_db as db:
            stmt = (
                select(
                    UserLocationRolEntity.id.label("user_location_rol_id"),
                    UserLocationRolEntity.location_id.label("location_id"),
                    UserEntity.id.label("user_id"),
                    UserEntity.email,
                    UserEntity.identification,
                    UserEntity.first_name,
                    UserEntity.last_name,
                    UserEntity.phone,
                    UserEntity.state.label("user_state"),
                    UserEntity.created_date.label("user_created_date"),
                    UserEntity.updated_date.label("user_updated_date"),
                    RolEntity.id.label("rol_id"),
                    RolEntity.name.label("rol_name"),
                    RolEntity.code.label("rol_code"),
                    RolEntity.description.label("rol_description"),
                )
                .join(UserEntity, UserLocationRolEntity.user_id == UserEntity.id)
                .join(RolEntity, UserLocationRolEntity.rol_id == RolEntity.id)
                .filter(UserLocationRolEntity.state == True)
                .order_by(UserEntity.first_name, UserEntity.last_name)
            )
            
            if not params.filters and not params.all_data:
                stmt = stmt.offset(params.skip).limit(params.limit)
            
            result = await db.execute(stmt)
            results = result.all()
            
            if not results:
                return None
            
            users_by_location: List[UserByLocationItem] = [
                map_to_user_by_location_item(row)
                for row in results
            ]
            
            if params.filters:
                alias_map = build_alias_map(response_class=UserByLocationItem)
                
                users_by_location = [
                    user
                    for user in users_by_location
                    if apply_memory_filters(user, params.filters, alias_map)
                ]
                
                if not params.all_data:
                    users_by_location = users_by_location[params.skip if params.skip else 0 : (params.skip if params.skip else 0) + (params.limit if params.limit else 10)]
            
            return users_by_location
```

**Archivo**: `src/infrastructure/database/repositories/business/__init__.py` (Crear si no existe)

```python
from .auth_repository import AuthRepository

__all__ = ["AuthRepository"]
```

---

### Use Case

**Archivo**: `src/domain/services/use_cases/business/auth/users_internal/users_internal_use_case.py`

```python
from typing import List, Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.wrappers.execute_transaction import execute_transaction

from src.domain.models.business.auth.list_users_by_location import (
    UserByLocationItem
)

from src.infrastructure.database.repositories.business.auth_repository import (
    AuthRepository
)


auth_repository = AuthRepository()


class UsersInternalUseCase:
    def __init__(self):
        self.auth_repository = auth_repository

    @execute_transaction(layer=LAYER.D_S_U_B.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[UserByLocationItem], None]:
        config.response_type = RESPONSE_TYPE.OBJECT
        
        users = await self.auth_repository.users_internal(
            config=config,
            params=params
        )
        
        return users
```

**Archivo**: `src/domain/services/use_cases/business/auth/users_internal/__init__.py`

```python
from .users_internal_use_case import UsersInternalUseCase

__all__ = ["UsersInternalUseCase"]
```

---

### Controller

**Archivo**: `src/infrastructure/web/controller/business/auth_controller.py` (Actualizar)

Agregar import:

```python
from src.core.models.filter import Pagination
from src.domain.models.business.auth.list_users_by_location import (
    UserByLocationItem
)
from src.domain.services.use_cases.business.auth.users_internal import (
    UsersInternalUseCase,
)
```

En el `__init__`:

```python
self.users_internal_use_case = UsersInternalUseCase()
```

Agregar método:

```python
@execute_transaction(layer=LAYER.I_W_C_B.value, enabled=settings.has_track)
async def users_internal(
    self, 
    config: Config, 
    params: Pagination
) -> Response[List[UserByLocationItem]]:
    result = await self.users_internal_use_case.execute(
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
from src.core.models.filter import Pagination
from src.domain.models.business.auth.list_users_by_location import (
    UserByLocationItem
)
```

Agregar endpoint:

```python
@auth_router.post(
    "/users-internal",
    status_code=status.HTTP_200_OK,
    response_model=Response[List[UserByLocationItem]]
)
@check_permissions([PERMISSION_TYPE.READ.value])
@execute_transaction_route(enabled=settings.has_track)
async def users_internal(
    params: Pagination,
    config: Config = Depends(get_config)
) -> Response[List[UserByLocationItem]]:
    return await auth_controller.users_internal(config=config, params=params)
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

**Flexibilidad Total:** El desarrollador puede filtrar por **cualquier campo que está en el response**. Si el campo se retorna en `UserByLocationItem`, entonces es filtrable. Puede combinar múltiples filtros según necesite.

**Ejemplo 1 - Usuarios de una ubicación específica (paginado):**
```json
{
  "skip": 0,
  "limit": 10,
  "all_data": false,
  "filters": [
    {
      "field": "location_id",
      "condition": "equals",
      "value": "660e8400-e29b-41d4-a716-446655440000"
    }
  ]
}
```
Retorna registros 1-10 de esa ubicación.

**Ejemplo 2 - Todos los administradores del sistema (sin paginación):**
```json
{
  "all_data": true,
  "filters": [
    {
      "field": "rol_code",
      "condition": "equals",
      "value": "ADMIN"
    }
  ]
}
```
Retorna TODOS los usuarios con rol ADMIN de TODAS las ubicaciones.

**Ejemplo 3 - Usuarios activos de múltiples ubicaciones:**
```json
{
  "skip": 0,
  "limit": 20,
  "filters": [
    {
      "field": "location_id",
      "condition": "in",
      "value": ["uuid-1", "uuid-2", "uuid-3"]
    },
    {
      "field": "user_state",
      "condition": "equals",
      "value": true
    }
  ]
}
```
Retorna usuarios activos de 3 ubicaciones específicas.

### Ejemplos de Filtros por Tipo de Campo

Recuerda: **Cualquier campo del response es filtrable**. Aquí algunos ejemplos por tipo:

**Filtros por UUIDs:**
```json
{"field": "user_id", "condition": "equals", "value": "uuid"}
{"field": "location_id", "condition": "in", "value": ["uuid1", "uuid2"]}
{"field": "rol_id", "condition": "equals", "value": "uuid"}
```

**Filtros por Strings:**
```json
{"field": "email", "condition": "like", "value": "@goluti"}
{"field": "first_name", "condition": "like", "value": "Juan"}
{"field": "rol_code", "condition": "equals", "value": "ADMIN"}
```

**Filtros por Boolean:**
```json
{"field": "user_state", "condition": "equals", "value": true}
```

**Filtros por Fechas:**
```json
{"field": "user_created_date", "condition": "gte", "value": "2024-01-01T00:00:00Z"}
{"field": "user_updated_date", "condition": "lt", "value": "2024-12-31T23:59:59Z"}
```

**Ejemplo 4 - Búsqueda con múltiples criterios:**
```json
{
  "skip": 0,
  "limit": 10,
  "filters": [
    {
      "field": "location_id",
      "condition": "equals",
      "value": "660e8400-e29b-41d4-a716-446655440000"
    },
    {
      "field": "first_name",
      "condition": "like",
      "value": "María"
    },
    {
      "field": "rol_code",
      "condition": "in",
      "value": ["ADMIN", "MANAGER"]
    },
    {
      "field": "user_state",
      "condition": "equals",
      "value": true
    }
  ]
}
```
Busca usuarios activos llamados "María" con rol ADMIN o MANAGER en esa ubicación específica.

---

## Manejo de Errores

| Error | Código HTTP | Descripción |
|-------|-------------|-------------|
| Sin autenticación | 401 | Token JWT no proporcionado o inválido |
| Sin permisos | 403 | Usuario no tiene permiso READ |
| Location no existe | 200 | Retorna array vacío |
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

---

## Ejemplos de Uso

### Caso 1: Listar usuarios de una ubicación específica

**Request:**
```bash
curl -X POST https://api.goluti.com/auth/users-internal \
  -H "Authorization: Bearer TOKEN" \
  -H "Language: es" \
  -H "Content-Type: application/json" \
  -d '{
    "skip": 0,
    "limit": 10,
    "filters": [
      {
        "field": "location_id",
        "condition": "equals",
        "value": "660e8400-e29b-41d4-a716-446655440000"
      }
    ]
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
      "user_location_rol_id": "aa0e8400",
      "location_id": "660e8400",
      "user_id": "bb0e8400",
      "email": "juan@goluti.com",
      "identification": "12345678",
      "first_name": "Juan",
      "last_name": "Pérez",
      "phone": "+573001234567",
      "user_state": true,
      "user_created_date": "2024-01-15T10:30:00Z",
      "user_updated_date": "2024-01-15T10:30:00Z",
      "rol_id": "880e8400",
      "rol_name": "Administrador",
      "rol_code": "ADMIN",
      "rol_description": "Administrador del sistema"
    }
  ]
}
```

### Caso 2: Listar TODOS los administradores del sistema (sin filtro de ubicación)

**Request:**
```bash
curl -X POST https://api.goluti.com/auth/users-internal \
  -H "Authorization: Bearer TOKEN" \
  -H "Language: es" \
  -H "Content-Type: application/json" \
  -d '{
    "all_data": true,
    "filters": [
      {
        "field": "rol_code",
        "condition": "equals",
        "value": "ADMIN"
      }
    ]
  }'
```

### Caso 3: Buscar usuarios por nombre en múltiples ubicaciones

**Request:**
```bash
curl -X POST https://api.goluti.com/auth/users-internal \
  -H "Authorization: Bearer TOKEN" \
  -H "Language: es" \
  -H "Content-Type: application/json" \
  -d '{
    "skip": 0,
    "limit": 10,
    "filters": [
      {
        "field": "location_id",
        "condition": "in",
        "value": ["660e8400-...", "770e8400-..."]
      },
      {
        "field": "first_name",
        "condition": "like",
        "value": "María"
      }
    ]
  }'
```

---

## Testing

### Tests Unitarios

**Archivo**: `tests/domain/services/use_cases/business/auth/users_internal/test_users_internal_use_case.py`

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.core.models.filter import Pagination, FilterManager
from src.core.enums.condition_type import CONDITION_TYPE
from src.domain.services.use_cases.business.auth.users_internal import (
    UsersInternalUseCase
)

@pytest.mark.asyncio
async def test_users_internal_success():
    use_case = UsersInternalUseCase()
    config = MagicMock()
    
    request = Pagination(
        skip=0,
        limit=10,
        filters=[
            FilterManager(
                field="location_id", 
                condition=CONDITION_TYPE.EQUALS, 
                value="uuid"
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
async def test_users_internal_endpoint(client: AsyncClient, admin_token):
    response = await client.post(
        "/auth/users-internal",
        headers={"Authorization": f"Bearer {admin_token}", "Language": "es"},
        json={
            "skip": 0,
            "limit": 10,
            "filters": [
                {
                    "field": "location_id",
                    "condition": "equals",
                    "value": "660e8400-e29b-41d4-a716-446655440000"
                }
            ]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["notification_type"] == "success"
    assert isinstance(data["response"], list)
```

---

## Consideraciones Técnicas

### Performance
- ✅ **JOIN Optimizado**: Consulta directa con JOINs en BD
- ✅ **Filtros en Memoria**: Usando helpers del core (`apply_memory_filters`, `build_alias_map`)
- ✅ **Paginación**: Aplicada después de filtros en memoria
- ✅ **Índices**: Requiere índices en `location_id`, `user_id`, `rol_id`

### Escalabilidad
- ✅ **Limit máximo**: 100 registros por página
- ✅ **Query eficiente**: Sin N+1 queries
- ✅ **Filtros en memoria**: Usando `apply_memory_filters` y `build_alias_map` (patrón del proyecto)

### Mejoras Futuras
1. **Cache**: Cachear resultados frecuentes
2. **Filtros avanzados**: OR lógico, rangos de fechas
3. **Ordenamiento**: Permitir ordenar por diferentes campos
4. **Exportación**: Generar CSV/Excel
5. **Estadísticas**: Total de usuarios por rol
6. **Constraint DB**: Agregar UNIQUE constraint en (user_id, location_id) si no existe

### Constraint de Base de Datos Recomendado

Para garantizar que un usuario solo pueda tener un rol por ubicación, se recomienda agregar un constraint único:

```sql
ALTER TABLE user_location_rol 
ADD CONSTRAINT unique_user_location 
UNIQUE (user_id, location_id);
```

Este constraint garantiza a nivel de base de datos que no se puedan crear asignaciones duplicadas de usuario-ubicación.

---

## Historial de Cambios

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0 | Nov 10, 2024 | Creación inicial de especificación. Endpoint: `/auth/users-internal`. Método: `users_internal()`. **Usa directamente clase `Pagination` del core** sin crear modelo request personalizado (reutilización de código). Query con JOINs entre user_location_rol, user y rol. **⚡ Optimización de paginación dual**: Si NO hay filtros → Paginación en SQL (offset/limit); Si HAY filtros → Paginación en memoria (después de filtrar). Sistema de filtros **flexible y genérico** - **el desarrollador puede filtrar por CUALQUIER campo del response** (todos los 15 campos de `UserByLocationItem` son filtrables automáticamente). `location_id` es opcional, se filtra mediante `filters`. Filtros aplicados en memoria usando `apply_memory_filters` y `build_alias_map`. Password excluido de respuesta. Regla de negocio: Un usuario tiene UN SOLO rol por ubicación. Requiere autenticación y permiso READ. | Equipo de Desarrollo Goluti |
| 1.1 | Nov 11, 2024 | **Corrección**: Nombre de clase en Repository de `AuthBusinessRepository` a `AuthRepository` (nombre correcto de la clase existente). Actualizado en: Repository, Use Case, `__init__.py` | Equipo de Desarrollo Goluti |

---

**Fin del Documento**


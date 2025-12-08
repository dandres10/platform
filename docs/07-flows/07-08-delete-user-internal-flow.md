# Flujo de Eliminación de Usuario Interno (Delete User Internal)

**Versión**: 1.0  
**Fecha**: Diciembre 2024  
**Estado**: Especificado  
**Autor(es)**: Equipo de Desarrollo Goluti  
**Responsable**: [Nombre del líder técnico]

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Objetivo](#objetivo)
3. [Contexto de Negocio](#contexto-de-negocio)
4. [Actores Involucrados](#actores-involucrados)
5. [Diagrama de Flujo](#diagrama-de-flujo)
6. [Especificación Técnica](#especificación-técnica)
7. [Endpoints API](#endpoints-api)
8. [Modelos de Datos](#modelos-de-datos)
9. [Validaciones y Reglas](#validaciones-y-reglas)
10. [Casos de Uso Involucrados](#casos-de-uso-involucrados)
11. [Manejo de Errores](#manejo-de-errores)
12. [Seguridad](#seguridad)
13. [Ejemplos de Uso](#ejemplos-de-uso)
14. [Referencias](#referencias)
15. [Historial de Cambios](#historial-de-cambios)

---

## Introducción

El flujo de **Delete User Internal** permite la eliminación completa de usuarios internos del sistema, aplicando el flujo inverso al de creación. Este endpoint elimina de manera atómica todas las entidades relacionadas que fueron creadas durante el proceso de alta del usuario interno.

Este flujo está basado en el proceso inverso de [Create User Internal](./07-01-create-user-internal-flow.md).

---

## Objetivo

Proporcionar un endpoint único que permita eliminar un usuario interno completo del sistema, ejecutando las siguientes operaciones de manera atómica (flujo inverso a la creación):

1. Validar que el usuario existe y puede ser eliminado
2. Verificar que el usuario no tiene relaciones activas adicionales (fuera de las de creación)
3. Eliminar todos los registros de `user_location_rol` asociados al usuario
4. Eliminar el registro del `user`
5. Eliminar el registro de `platform` asociado

### Alcance

**En alcance:**
- Eliminación de registros `user_location_rol` asociados al usuario
- Eliminación del registro `user`
- Eliminación de la configuración de `platform` asociada
- Validación de relaciones activas que impidan la eliminación
- Validaciones de integridad referencial
- Transaccionalidad del proceso completo (rollback si falla algún paso)

**Fuera de alcance:**
- Eliminación de datos históricos o logs del usuario
- Notificación por email de eliminación
- Soft delete (se realiza hard delete)
- Eliminación de usuarios externos (flujo separado)

---

## Contexto de Negocio

### Problema que Resuelve

Actualmente, eliminar un usuario interno requiere múltiples llamadas a diferentes endpoints en orden específico:
1. `DELETE /user_location_rol` - Eliminar cada asignación de rol (N veces)
2. `DELETE /user` - Eliminar usuario
3. `DELETE /platform` - Eliminar configuración de plataforma

Este flujo unifica todo en una sola operación atómica, garantizando consistencia y simplificando el proceso. Además, valida automáticamente que el usuario no tenga relaciones activas que impidan su eliminación.

**Regla de Negocio Importante**: Un usuario interno NO puede ser eliminado físicamente si tiene relaciones activas en otras tablas del sistema (como órdenes, transacciones, etc.). En tal caso, se realiza un **soft delete** (inactivación) actualizando el campo `state` a `false`, y se informa al usuario que no pudo ser eliminado pero fue inactivado. Después de 1 mes será eliminado permanentemente.

### Beneficios Esperados

- ✅ Simplificación del proceso de baja de usuarios
- ✅ Garantía de atomicidad (todo o nada)
- ✅ Reducción de errores por proceso manual
- ✅ Validaciones centralizadas de relaciones activas
- ✅ Prevención de eliminación de usuarios con flujos activos
- ✅ Limpieza completa de datos relacionados
- ✅ Mejor experiencia para administradores

---

## Actores Involucrados

| Actor | Rol | Responsabilidad |
|-------|-----|-----------------|
| **Super Administrador** | Admin del sistema | Eliminar usuarios internos |
| **Sistema** | Automático | Validar datos, eliminar registros, verificar relaciones |

---

## Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────────┐
│                    Request DELETE /auth/delete-user-internal    │
│  {                                                               │
│    user_id: UUID                                                │
│  }                                                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    1. VALIDAR USUARIO EXISTE                     │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ UserReadUseCase.execute({id: user_id})                    │  │
│  │                                                            │  │
│  │ Si no existe → ERROR: "Usuario no encontrado"             │  │
│  │ Si existe → Continuar                                     │  │
│  │                                                            │  │
│  │ → user: User (con platform_id)                            │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              2. VERIFICAR RELACIONES ACTIVAS                     │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Consultar otras tablas que referencien user_id:           │  │
│  │                                                            │  │
│  │ Tablas a verificar (extensible en el futuro):             │  │
│  │   - [Otras tablas que puedan tener user_id]               │  │
│  │                                                            │  │
│  │ Si existe alguna relación activa:                         │  │
│  │   → ERROR: "Usuario relacionado a flujos activos"         │  │
│  │                                                            │  │
│  │ Si no hay relaciones activas → Continuar                  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│         3. OBTENER REGISTROS USER_LOCATION_ROL                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ UserLocationRolListUseCase.execute({                      │  │
│  │   filters: [                                              │  │
│  │     { field: "user_id", condition: EQUALS, value: id }    │  │
│  │   ]                                                       │  │
│  │ })                                                        │  │
│  │                                                            │  │
│  │ → user_location_rols: List[UserLocationRol]               │  │
│  │   (puede ser lista vacía si no tiene asignaciones)        │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│         4. ELIMINAR REGISTROS USER_LOCATION_ROL (LOOP)           │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Para cada registro en user_location_rols:                 │  │
│  │                                                            │  │
│  │   UserLocationRolDeleteUseCase.execute({                  │  │
│  │     id: user_location_rol.id                              │  │
│  │   })                                                       │  │
│  │                                                            │  │
│  │ Ejemplo (si tenía 2 asignaciones):                        │  │
│  │   - Eliminar ULR con Sede A + Rol Admin  ✓                │  │
│  │   - Eliminar ULR con Sede B + Rol Operador ✓              │  │
│  │                                                            │  │
│  │ Si falla alguna eliminación → ROLLBACK completo           │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    5. ELIMINAR USUARIO                           │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ UserDeleteUseCase.execute({                               │  │
│  │   id: user_id                                             │  │
│  │ })                                                         │  │
│  │                                                            │  │
│  │ Guarda platform_id antes de eliminar para paso 6          │  │
│  │                                                            │  │
│  │ Si falla → ROLLBACK completo                              │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    6. ELIMINAR PLATFORM                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ PlatformDeleteUseCase.execute({                           │  │
│  │   id: platform_id (guardado del paso 1)                   │  │
│  │ })                                                         │  │
│  │                                                            │  │
│  │ Si falla → ROLLBACK completo                              │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              7. RETORNAR MENSAJE DE ÉXITO                        │
│  {                                                               │
│    message_type: "temporary",                                    │
│    notification_type: "success",                                 │
│    message: "Usuario interno eliminado exitosamente",           │
│    response: null                                                │
│  }                                                               │
│                                                                  │
│  Nota: El mensaje es traducido usando KEYS_MESSAGES              │
│        según el idioma configurado en el header                  │
└─────────────────────────────────────────────────────────────────┘
```

### Comparación: Flujo Creación vs Eliminación

| Paso | Creación | Eliminación (Inverso) |
|------|----------|----------------------|
| 1 | Validar referencias (language, currency, locations, roles) | Validar que usuario existe |
| 2 | - | Verificar relaciones activas |
| 3 | Crear Platform | Obtener UserLocationRol(s) |
| 4 | Crear User | Eliminar UserLocationRol(s) |
| 5 | Crear UserLocationRol(s) | Eliminar User |
| 6 | Retornar éxito | Eliminar Platform |
| 7 | - | Retornar éxito |

### Estados del Flujo

| Estado | Descripción | Siguiente Estado |
|--------|-------------|-----------------|
| **VALIDATING_USER** | Validando que usuario existe | CHECKING_RELATIONS, ERROR |
| **CHECKING_RELATIONS** | Verificando relaciones activas | FETCHING_ROLES, ERROR |
| **FETCHING_ROLES** | Obteniendo asignaciones de rol | DELETING_ROLES, ERROR |
| **DELETING_ROLES** | Eliminando user_location_rol | DELETING_USER, ERROR |
| **DELETING_USER** | Eliminando registro de usuario | DELETING_PLATFORM, ERROR |
| **DELETING_PLATFORM** | Eliminando configuración de plataforma | COMPLETED, ERROR |
| **COMPLETED** | Usuario eliminado exitosamente | - |
| **ERROR** | Error en algún paso (rollback) | - |

---

## Especificación Técnica

### Arquitectura

```
┌──────────────────────────────────────────────────────────────┐
│         Infrastructure/Web Layer                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  DELETE /auth/delete-user-internal                     │  │
│  │  - AuthRouter                                          │  │
│  │  - @check_permissions([PERMISSION_TYPE.DELETE])        │  │
│  │  - @check_roles(["ADMIN"])                             │  │
│  │  - @execute_transaction_route                          │  │
│  └──────────────────────┬─────────────────────────────────┘  │
└─────────────────────────┼────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│         Infrastructure/Web/Controller Layer                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  AuthController.delete_user_internal()                 │  │
│  │  - Invoca Use Case                                     │  │
│  │  - Construye Response                                  │  │
│  └──────────────────────┬─────────────────────────────────┘  │
└─────────────────────────┼────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│              Domain/Business Use Case Layer                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  DeleteUserInternalUseCase.execute()                   │  │
│  │  ├─ 1. UserReadUseCase (validar existencia)            │  │
│  │  │                                                      │  │
│  │  ├─ 2. Verificar relaciones activas                    │  │
│  │  │    └─ [Consultas a otras tablas si aplica]          │  │
│  │  │                                                      │  │
│  │  ├─ 3. UserLocationRolListUseCase (obtener registros)  │  │
│  │  │                                                      │  │
│  │  ├─ 4. UserLocationRolDeleteUseCase (N veces)          │  │
│  │  │                                                      │  │
│  │  ├─ 5. UserDeleteUseCase                               │  │
│  │  │                                                      │  │
│  │  └─ 6. PlatformDeleteUseCase                           │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### Componentes Principales

#### 1. Models (`src/domain/models/business/auth/delete_user_internal/`)

**Archivos a crear:**
- `delete_user_internal_request.py`
- `index.py`

#### 2. Use Case (`src/domain/services/use_cases/business/auth/delete_user_internal/`)

**Archivo a crear:**
- `delete_user_internal_use_case.py`

#### 3. Controller (actualizar existente)

**Archivo a actualizar:**
- `src/infrastructure/web/controller/business/auth_controller.py`

#### 4. Router (actualizar existente)

**Archivo a actualizar:**
- `src/infrastructure/web/business_routes/auth_router.py`

---

## Endpoints API

### Endpoint: Delete User Internal

```
DELETE /auth/delete-user-internal/{user_id}
```

**Headers:**
```
Authorization: Bearer <token>
Language: es | en
```

**Restricciones de Acceso:**
- ⚠️ **Rol requerido**: `ADMIN` (solo administradores)
- **Permiso requerido**: `PERMISSION_TYPE.DELETE`
- **Autenticación**: Token JWT válido

**Path Parameters:**
| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `user_id` | UUID | Sí | ID del usuario interno a eliminar |

**Ejemplo de URL:**
```
DELETE /auth/delete-user-internal/550e8400-e29b-41d4-a716-446655440000
```

**Response (Success - 200 OK):**
```json
{
  "message_type": "temporary",
  "notification_type": "success",
  "message": "Usuario interno eliminado exitosamente",
  "response": null
}
```

**Nota:** El campo `response` es `null` para este endpoint. El mensaje de éxito se obtiene del sistema de traducción usando `KEYS_MESSAGES.AUTH_DELETE_USER_SUCCESS`.

**Response (Error - Usuario No Encontrado):**
```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "El usuario con ID 550e8400-e29b-41d4-a716-446655440000 no existe en el sistema",
  "response": null
}
```

**Response (Soft Delete - Usuario con Relaciones Activas):**
```json
{
  "message_type": "static",
  "notification_type": "warning",
  "message": "El usuario tiene relaciones activas y no pudo ser eliminado, pero fue inactivado. Será eliminado permanentemente después de 1 mes",
  "response": null
}
```

**Nota**: Cuando el usuario tiene relaciones activas, se realiza un **soft delete** (se actualiza `state = false`), en lugar de retornar solo un error. El usuario quedará inactivo y será eliminado permanentemente después de 1 mes.

**Response (Error - No Puede Eliminarse a Sí Mismo):**
```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "No puede eliminar su propio usuario",
  "response": null
}
```

**Response (Error - Rol No Autorizado - 403):**
```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "Solo usuarios con rol ADMIN pueden eliminar usuarios internos",
  "response": null
}
```

**Response (Error - Sin Permisos - 403):**
```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "No tiene permisos para realizar esta acción",
  "response": null
}
```

**Códigos de Estado:**
- **200 OK**: Usuario eliminado exitosamente
- **200 OK + error**: Error de validación o negocio (usuario no existe, relaciones activas, etc.)
- **401 Unauthorized**: Token inválido o expirado
- **403 Forbidden**: Rol no autorizado (no es ADMIN) o sin permisos (no tiene permiso DELETE)
- **422 Unprocessable Entity**: Error de validación Pydantic (formato de UUID incorrecto)

---

## Modelos de Datos

### Request Model

**Archivo**: `src/domain/models/business/auth/delete_user_internal/delete_user_internal_request.py`

```python
from pydantic import BaseModel, Field, UUID4


class DeleteUserInternalRequest(BaseModel):
    user_id: UUID4 = Field(..., description="ID del usuario interno a eliminar")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }
```

### Index File

**Archivo**: `src/domain/models/business/auth/delete_user_internal/index.py`

```python
from .delete_user_internal_request import DeleteUserInternalRequest

__all__ = [
    "DeleteUserInternalRequest"
]
```

**Nota**: Solo se exporta el modelo de Request. No hay modelo de Response porque el endpoint retorna `response: null`.

---

## Validaciones y Reglas

### Reglas de Negocio

1. **Usuario Existe**: El `user_id` debe existir en la tabla `user`
2. **Sin Relaciones Activas**: El usuario no debe tener relaciones activas en otras tablas del sistema (fuera de las creadas en el flujo de alta)
3. **No Auto-Eliminación**: Un administrador no puede eliminar su propio usuario
4. **Mismo Location**: El usuario a eliminar debe pertenecer a la misma ubicación del administrador (`config.token.location_id`)
5. **No Último Admin**: Si el usuario a eliminar es el único con rol `ADMIN` en la ubicación, no se puede eliminar. Se debe crear o asignar rol de administrador a otro usuario primero.
6. **Eliminación Completa**: Se eliminan TODOS los registros de `user_location_rol`, `user` y `platform`
7. **Atomicidad**: Si falla algún paso de eliminación, se debe hacer rollback de toda la operación
8. **Solo Usuarios Internos**: Este endpoint solo aplica para usuarios internos (creados con create-user-internal)

### Validaciones Técnicas

**Nota importante**: Todos los mensajes de error usan el sistema de traducciones del proyecto mediante `KEYS_MESSAGES` y `Message().get_message()`.

#### 1. Validación de Usuario Existe

```python
user = await self.user_read_uc.execute(
    config=config,
    params=UserRead(id=params.user_id)
)

if isinstance(user, str) or not user:
    return await self.message.get_message(
        config=config,
        message=MessageCoreEntity(
            key=KEYS_MESSAGES.AUTH_DELETE_USER_NOT_FOUND.value,
            params={"user_id": str(params.user_id)}
        ),
    )
```

#### 2. Validación de No Auto-Eliminación

```python
if str(params.user_id) == str(config.token.user_id):
    return await self.message.get_message(
        config=config,
        message=MessageCoreEntity(
            key=KEYS_MESSAGES.AUTH_DELETE_USER_CANNOT_DELETE_SELF.value
        ),
    )
```

#### 3. Validación de Relaciones Activas

```python
has_active_relations = await self._check_active_relations(
    config=config,
    user_id=params.user_id
)

if has_active_relations:
    return await self.message.get_message(
        config=config,
        message=MessageCoreEntity(
            key=KEYS_MESSAGES.AUTH_DELETE_USER_HAS_ACTIVE_RELATIONS.value
        ),
    )
```

**Método privado para verificar relaciones:**

```python
async def _check_active_relations(
    self,
    config: Config,
    user_id: UUID4
) -> bool:
    """
    Verifica si el usuario tiene relaciones activas que impidan su eliminación.
    
    Actualmente verifica:
    - (Agregar tablas futuras que referencien user_id)
    
    Returns:
        bool: True si tiene relaciones activas, False si puede ser eliminado
    """
    # Por ahora solo tiene user_location_rol que se elimina en el flujo
    # Cuando se agreguen otras tablas (ordenes, transacciones, etc.)
    # se debe agregar la verificación aquí
    
    # Ejemplo de cómo agregar verificación futura:
    # orders = await self.order_list_uc.execute(
    #     config=config,
    #     params=Pagination(
    #         filters=[
    #             FilterManager(
    #                 field="user_id",
    #                 condition=CONDITION_TYPE.EQUALS,
    #                 value=str(user_id)
    #             )
    #         ]
    #     )
    # )
    # if orders and not isinstance(orders, str):
    #     return True
    
    return False
```

### Nuevas Claves de Traducción Requeridas

**Archivo**: `src/core/enums/keys_message.py`

Agregar las siguientes claves al enum `KEYS_MESSAGES`:

```python
AUTH_DELETE_USER_NOT_FOUND = "auth_delete_user_not_found"
AUTH_DELETE_USER_CANNOT_DELETE_SELF = "auth_delete_user_cannot_delete_self"
AUTH_DELETE_USER_HAS_ACTIVE_RELATIONS = "auth_delete_user_has_active_relations"
AUTH_DELETE_USER_NOT_IN_LOCATION = "auth_delete_user_not_in_location"
AUTH_DELETE_USER_LAST_ADMIN = "auth_delete_user_last_admin"
AUTH_DELETE_USER_SUCCESS = "auth_delete_user_success"
AUTH_DELETE_USER_ERROR_DELETING_ROLES = "auth_delete_user_error_deleting_roles"
AUTH_DELETE_USER_ERROR_DELETING_USER = "auth_delete_user_error_deleting_user"
AUTH_DELETE_USER_ERROR_DELETING_PLATFORM = "auth_delete_user_error_deleting_platform"
```

**Traducciones necesarias en la tabla `translation`:**

| Key | Context | ES (Español) | EN (English) |
|-----|---------|--------------|--------------|
| `auth_delete_user_not_found` | auth | El usuario con ID {user_id} no existe en el sistema | The user with ID {user_id} does not exist in the system |
| `auth_delete_user_cannot_delete_self` | auth | No puede eliminar su propio usuario | You cannot delete your own user |
| `auth_delete_user_has_active_relations` | auth | El usuario está relacionado a flujos activos y no puede ser eliminado | The user is related to active flows and cannot be deleted |
| `auth_delete_user_not_in_location` | auth | El usuario no pertenece a su ubicación y no puede ser eliminado | The user does not belong to your location and cannot be deleted |
| `auth_delete_user_last_admin` | auth | Este usuario es el único administrador de esta ubicación. Debe crear o asignar rol de administrador a otro usuario antes de poder eliminarlo | This user is the only administrator for this location. You must create or assign the administrator role to another user before you can delete this one |
| `auth_delete_user_error_fetching_roles` | auth | Error al obtener los roles del usuario | Error fetching user roles |
| `auth_delete_user_no_roles_found` | auth | El usuario no tiene roles asignados. Esto indica un problema de integridad de datos | The user has no assigned roles. This indicates a data integrity issue |
| `auth_delete_user_soft_deleted` | auth | El usuario tiene relaciones activas y no pudo ser eliminado, pero fue inactivado. Será eliminado permanentemente después de 1 mes | The user has active relations and could not be deleted, but was deactivated. It will be permanently deleted after 1 month |
| `auth_delete_user_error_soft_delete` | auth | Error al inactivar el usuario | Error deactivating user |
| `auth_delete_user_success` | auth | Usuario interno eliminado exitosamente | Internal user deleted successfully |
| `auth_delete_user_error_deleting_roles` | auth | Error al eliminar las asignaciones de rol del usuario | Error deleting user role assignments |
| `auth_delete_user_error_deleting_user` | auth | Error al eliminar el usuario | Error deleting user |
| `auth_delete_user_error_deleting_platform` | auth | Error al eliminar la configuración de plataforma | Error deleting platform configuration |

**Nota**: Las traducciones con `{placeholders}` soportan interpolación de parámetros.

### Migración SQL

**Archivo**: `migrations/changelog-v31.sql`

La migración incluye todas las traducciones en español (es) e inglés (en) para el flujo de eliminación de usuario interno.

```sql
-- liquibase formatted sql
-- changeset delete-user-internal-translations:1733356800000-31

-- Errores de validación
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'auth_delete_user_not_found', 'es', 'El usuario con ID {user_id} no existe en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_not_found', 'en', 'The user with ID {user_id} does not exist in the system', 'backend', true, now(), now()),
-- ... (ver archivo completo)

--ROLLBACK DELETE FROM translation WHERE "key" LIKE 'auth_delete_user_%';
```

---

## Casos de Uso Involucrados

### Use Cases de Validación (Read/List)

| Use Case | Propósito | Cantidad de Ejecuciones |
|----------|-----------|-------------------------|
| `UserReadUseCase` | Validar que user_id existe y obtener platform_id | 1 vez |
| `UserLocationRolListUseCase` | Obtener todos los registros de rol del usuario | 1 vez |

### Use Cases de Eliminación (Delete)

| Use Case | Propósito | Cantidad de Ejecuciones |
|----------|-----------|-------------------------|
| `UserLocationRolDeleteUseCase` | Eliminar cada asignación de rol | N veces (por cada registro) |
| `UserDeleteUseCase` | Eliminar el registro de usuario | 1 vez |
| `PlatformDeleteUseCase` | Eliminar configuración de plataforma | 1 vez |

**Nota**: Si el usuario tenía 3 asignaciones en `user_location_rol`, se ejecutarán 3 eliminaciones de ese tipo.

---

## Use Case Principal

**Archivo**: `src/domain/services/use_cases/business/auth/delete_user_internal/delete_user_internal_use_case.py`

```python
from typing import Union
from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination, FilterManager
from src.core.enums.condition_type import CONDITION_TYPE
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.wrappers.execute_transaction import execute_transaction
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity

from src.domain.models.business.auth.delete_user_internal.index import (
    DeleteUserInternalRequest
)
from src.domain.models.entities.user.index import UserRead, UserDelete
from src.domain.models.entities.user_location_rol.index import UserLocationRolDelete
from src.domain.models.entities.platform.index import PlatformDelete

from src.domain.services.use_cases.entities.user.user_read_use_case import (
    UserReadUseCase
)
from src.domain.services.use_cases.entities.user.user_delete_use_case import (
    UserDeleteUseCase
)
from src.domain.services.use_cases.entities.user_location_rol.user_location_rol_list_use_case import (
    UserLocationRolListUseCase
)
from src.domain.services.use_cases.entities.user_location_rol.user_location_rol_delete_use_case import (
    UserLocationRolDeleteUseCase
)
from src.domain.services.use_cases.entities.platform.platform_delete_use_case import (
    PlatformDeleteUseCase
)

from src.infrastructure.database.repositories.entities.user_repository import (
    UserRepository
)
from src.infrastructure.database.repositories.entities.user_location_rol_repository import (
    UserLocationRolRepository
)
from src.infrastructure.database.repositories.entities.platform_repository import (
    PlatformRepository
)


user_repository = UserRepository()
user_location_rol_repository = UserLocationRolRepository()
platform_repository = PlatformRepository()


class DeleteUserInternalUseCase:
    def __init__(self):
        self.user_read_uc = UserReadUseCase(user_repository)
        self.user_delete_uc = UserDeleteUseCase(user_repository)
        self.user_location_rol_list_uc = UserLocationRolListUseCase(
            user_location_rol_repository
        )
        self.user_location_rol_delete_uc = UserLocationRolDeleteUseCase(
            user_location_rol_repository
        )
        self.platform_delete_uc = PlatformDeleteUseCase(platform_repository)
        
        self.message = Message()
    
    async def _check_active_relations(
        self,
        config: Config,
        user_id: UUID4
    ) -> bool:
        # Extensible: agregar verificaciones de otras tablas aquí
        # Por ahora retorna False (sin relaciones adicionales)
        return False
    
    @execute_transaction(layer=LAYER.D_S_U_B.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: DeleteUserInternalRequest,
    ) -> Union[str, None]:
        
        config.response_type = RESPONSE_TYPE.OBJECT
        
        user = await self.user_read_uc.execute(
            config=config,
            params=UserRead(id=params.user_id)
        )
        if isinstance(user, str) or not user:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_DELETE_USER_NOT_FOUND.value,
                    params={"user_id": str(params.user_id)}
                ),
            )
        
        platform_id = user.platform_id
        
        if str(params.user_id) == str(config.token.user_id):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_DELETE_USER_CANNOT_DELETE_SELF.value
                ),
            )
        
        has_active_relations = await self._check_active_relations(
            config=config,
            user_id=params.user_id
        )
        if has_active_relations:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_DELETE_USER_HAS_ACTIVE_RELATIONS.value
                ),
            )
        
        user_location_rols = await self.user_location_rol_list_uc.execute(
            config=config,
            params=Pagination(
                filters=[
                    FilterManager(
                        field="user_id",
                        condition=CONDITION_TYPE.EQUALS,
                        value=str(params.user_id)
                    )
                ]
            )
        )
        
        if user_location_rols and not isinstance(user_location_rols, str):
            for ulr in user_location_rols:
                delete_result = await self.user_location_rol_delete_uc.execute(
                    config=config,
                    params=UserLocationRolDelete(id=ulr.id)
                )
                if isinstance(delete_result, str):
                    return await self.message.get_message(
                        config=config,
                        message=MessageCoreEntity(
                            key=KEYS_MESSAGES.AUTH_DELETE_USER_ERROR_DELETING_ROLES.value
                        ),
                    )
        
        user_deleted = await self.user_delete_uc.execute(
            config=config,
            params=UserDelete(id=params.user_id)
        )
        if isinstance(user_deleted, str):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_DELETE_USER_ERROR_DELETING_USER.value
                ),
            )
        
        platform_deleted = await self.platform_delete_uc.execute(
            config=config,
            params=PlatformDelete(id=platform_id)
        )
        if isinstance(platform_deleted, str):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_DELETE_USER_ERROR_DELETING_PLATFORM.value
                ),
            )
        
        return None
```

---

### Controller

**Archivo**: `src/infrastructure/web/controller/business/auth_controller.py`

Agregar el método al controlador existente:

```python
@execute_transaction(layer=LAYER.I_W_C_B.value, enabled=settings.has_track)
async def delete_user_internal(
    self, 
    config: Config, 
    params: DeleteUserInternalRequest
) -> Response[None]:
    result = await self.delete_user_internal_use_case.execute(
        config=config, 
        params=params
    )
    
    if isinstance(result, str):
        return Response.error(None, result)
    
    return Response.success_temporary_message(
        response=None,
        message=await self.message.get_message(
            config=config,
            message=MessageCoreEntity(
                key=KEYS_MESSAGES.AUTH_DELETE_USER_SUCCESS.value
            ),
        ),
    )
```

**Lógica del Controller:**
- Si el Use Case retorna `str` → Error → `Response.error(None, result)`
- Si el Use Case retorna `None` → Éxito → `Response.success_temporary_message(response=None, message=...)`

---

### Router

**Archivo**: `src/infrastructure/web/business_routes/auth_router.py`

Agregar el endpoint al router existente:

```python
@auth_router.delete(
    "/delete-user-internal/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=Response[None]
)
@check_permissions([PERMISSION_TYPE.DELETE.value])
@check_roles(["ADMIN"])
@execute_transaction_route(enabled=settings.has_track)
async def delete_user_internal(
    user_id: UUID = Path(..., description="ID del usuario interno a eliminar"),
    config: Config = Depends(get_config)
) -> Response[None]:
    return await auth_controller.delete_user_internal(config=config, user_id=user_id)
```

**Nota**: El `user_id` se recibe como path parameter en la URL. El `response_model` es `Response[None]` porque el campo `response` será `null`.

---

## Manejo de Errores

| Error | Código HTTP | Mensaje | Solución |
|-------|-------------|---------|----------|
| Usuario no existe | 200 | "El usuario con ID {id} no existe en el sistema" | Verificar user_id |
| Auto-eliminación | 200 | "No puede eliminar su propio usuario" | Usar otro admin para eliminar |
| Relaciones activas | 200 | "El usuario está relacionado a flujos activos y no puede ser eliminado" | Resolver relaciones pendientes |
| Ubicación diferente | 200 | "El usuario no pertenece a su ubicación y no puede ser eliminado" | Solo puede eliminar usuarios de su misma ubicación |
| Error obteniendo roles | 200 | "Error al obtener los roles del usuario" | Revisar logs del sistema |
| Usuario sin roles | 200 | "El usuario no tiene roles asignados. Esto indica un problema de integridad de datos" | Verificar integridad de datos en user_location_rol |
| Error eliminando roles | 200 | "Error al eliminar las asignaciones de rol del usuario" | Revisar logs |
| Error eliminando user | 200 | "Error al eliminar el usuario" | Revisar logs |
| Error eliminando platform | 200 | "Error al eliminar la configuración de plataforma" | Revisar logs |
| Rol no autorizado | 403 | "Solo usuarios con rol ADMIN pueden eliminar usuarios internos" | Debe tener rol ADMIN |
| Sin permisos | 403 | "No tiene permisos para realizar esta acción" | Debe tener permiso DELETE |
| Token inválido | 401 | "Token inválido o expirado" | Renovar token |

**Nota importante sobre errores**:
- Todos los errores de validación retornan código 200 con mensaje descriptivo dentro del response estándar de la API.
- Si ocurre un error en cualquiera de las eliminaciones, se hace rollback de toda la transacción.
- El orden de eliminación es importante: primero `user_location_rol`, luego `user`, finalmente `platform`.

---

## Seguridad

### Permisos Requeridos

```python
@check_permissions([PERMISSION_TYPE.DELETE.value])
@check_roles(["ADMIN"])
```

**Restricción de Rol:**
- ⚠️ **Solo usuarios con rol `ADMIN`** pueden consumir este endpoint
- El rol debe estar activo y vigente
- El usuario debe tener el permiso `DELETE` asociado a su rol

### Validaciones de Seguridad

1. **Validación de Rol**: Solo rol `ADMIN` puede eliminar usuarios internos
2. **Validación de Permiso**: Requiere permiso `DELETE`
3. **Token JWT**: Validación en cada request
4. **No Auto-Eliminación**: Un admin no puede eliminarse a sí mismo
5. **Validación de Location**: El usuario a eliminar debe pertenecer a la misma ubicación del admin (`config.token.location_id`)
6. **Validación de Último Admin**: Si el usuario a eliminar tiene rol ADMIN y es el único en la ubicación, no se permite eliminarlo
7. **Auditoría**: El decorador `@execute_transaction` registra la operación con información del usuario admin que ejecuta la acción
8. **Rate Limiting**: Aplicar límite (ej: 5 eliminaciones/hora por admin)

### Lógica de Validación de Location

```python
# Validar que el usuario pertenezca a la misma ubicación del admin
admin_location_id = str(config.token.location_id)
user_belongs_to_location = False

if user_location_rols and not isinstance(user_location_rols, str):
    for ulr in user_location_rols:
        if str(ulr.location_id) == admin_location_id:
            user_belongs_to_location = True
            break

if not user_belongs_to_location:
    return await self.message.get_message(
        config=config,
        message=MessageCoreEntity(
            key=KEYS_MESSAGES.AUTH_DELETE_USER_NOT_IN_LOCATION.value
        ),
    )
```

### Consideraciones Adicionales

- **Hard Delete**: Este flujo realiza eliminación física de los registros
- **HTTPS**: Siempre usar en producción
- **Validación de entrada**: Pydantic valida formato UUID
- **Segregación de responsabilidades**: Solo administradores pueden eliminar usuarios internos
- **Trazabilidad**: Mantener logs de eliminaciones para auditoría

---

## Ejemplos de Uso

### Caso de Uso 1: Eliminar Usuario Exitosamente

**Escenario**: El administrador elimina al usuario Juan que ya no trabaja en la empresa.

**Request:**
```bash
curl -X DELETE "https://api.goluti.com/auth/delete-user-internal/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer TOKEN" \
  -H "Language: es"
```

**Response:**
```json
{
  "message_type": "temporary",
  "notification_type": "success",
  "message": "Usuario interno eliminado exitosamente",
  "response": null
}
```

### Caso de Uso 2: Error - Usuario No Encontrado

**Request:**
```bash
curl -X DELETE "https://api.goluti.com/auth/delete-user-internal/999e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer TOKEN" \
  -H "Language: es"
```

**Response:**
```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "El usuario con ID 999e8400-e29b-41d4-a716-446655440000 no existe en el sistema",
  "response": null
}
```

### Caso de Uso 3: Error - Usuario con Relaciones Activas

**Escenario**: El usuario tiene órdenes pendientes asociadas (ejemplo futuro).

**Request:**
```bash
curl -X DELETE "https://api.goluti.com/auth/delete-user-internal/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer TOKEN" \
  -H "Language: es"
```

**Response:**
```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "El usuario está relacionado a flujos activos y no puede ser eliminado",
  "response": null
}
```

### Caso de Uso 4: Error - Intentar Auto-Eliminación

**Request:**
```bash
curl -X DELETE "https://api.goluti.com/auth/delete-user-internal/ID_DEL_ADMIN_AUTENTICADO" \
  -H "Authorization: Bearer TOKEN" \
  -H "Language: es"
```

**Response:**
```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "No puede eliminar su propio usuario",
  "response": null
}
```

### Caso de Uso 5: Error - Sin Permisos (No es ADMIN)

**Request:**
```bash
curl -X DELETE "https://api.goluti.com/auth/delete-user-internal/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer TOKEN_USUARIO_NO_ADMIN" \
  -H "Language: es"
```

**Response (HTTP 403):**
```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "Solo usuarios con rol ADMIN pueden eliminar usuarios internos",
  "response": null
}
```

---

## Testing

### Estructura de Tests (Espejo)

La carpeta `tests` funciona como espejo de las carpetas `domain` e `infrastructure`:

```
src/tests/
├── domain/
│   └── services/
│       └── use_cases/
│           └── business/
│               └── auth/
│                   └── delete_user_internal/
│                       └── test_delete_user_internal_use_case.py
└── infrastructure/
    └── web/
        ├── controller/
        │   └── business/
        │       └── test_auth_controller.py
        └── business_routes/
            └── test_auth_router.py
```

### Unit Tests

**Archivo**: `src/tests/domain/services/use_cases/business/auth/delete_user_internal/test_delete_user_internal_use_case.py`

```python
import pytest
from src.domain.services.use_cases.business.auth.delete_user_internal.delete_user_internal_use_case import (
    DeleteUserInternalUseCase
)
from src.domain.models.business.auth.delete_user_internal.index import (
    DeleteUserInternalRequest
)

@pytest.mark.asyncio
async def test_delete_user_internal_success(mock_config, existing_user_id):
    """Test eliminación exitosa de usuario interno"""
    request = DeleteUserInternalRequest(user_id=existing_user_id)
    
    use_case = DeleteUserInternalUseCase()
    result = await use_case.execute(config=mock_config, params=request)
    
    assert result is None

@pytest.mark.asyncio
async def test_delete_user_internal_user_not_found(mock_config):
    """Test error: usuario no existe"""
    request = DeleteUserInternalRequest(
        user_id="999e8400-e29b-41d4-a716-446655440000"
    )
    
    use_case = DeleteUserInternalUseCase()
    result = await use_case.execute(config=mock_config, params=request)
    
    assert isinstance(result, str)
    assert "no existe" in result.lower()

@pytest.mark.asyncio
async def test_delete_user_internal_cannot_delete_self(mock_config_with_user):
    """Test error: no puede eliminar su propio usuario"""
    request = DeleteUserInternalRequest(
        user_id=mock_config_with_user.user_id
    )
    
    use_case = DeleteUserInternalUseCase()
    result = await use_case.execute(config=mock_config_with_user, params=request)
    
    assert isinstance(result, str)
    assert "propio" in result.lower() or "self" in result.lower()

@pytest.mark.asyncio
async def test_delete_user_internal_has_active_relations(mock_config, user_with_orders):
    """Test error: usuario con relaciones activas"""
    request = DeleteUserInternalRequest(user_id=user_with_orders)
    
    use_case = DeleteUserInternalUseCase()
    result = await use_case.execute(config=mock_config, params=request)
    
    assert isinstance(result, str)
    assert "activos" in result.lower() or "active" in result.lower()

@pytest.mark.asyncio
async def test_delete_user_internal_deletes_all_related_records(
    mock_config, 
    user_with_multiple_locations
):
    """Test que se eliminan todos los registros relacionados"""
    request = DeleteUserInternalRequest(user_id=user_with_multiple_locations)
    
    use_case = DeleteUserInternalUseCase()
    result = await use_case.execute(config=mock_config, params=request)
    
    assert result is None
    # Verificar que user_location_rol, user y platform fueron eliminados
```

### Integration Tests

**Archivo**: `src/tests/infrastructure/web/business_routes/test_auth_router.py`

```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_delete_user_internal_endpoint_success(client: TestClient, admin_token, user_to_delete):
    """Test endpoint completo con token de admin"""
    response = client.delete(
        "/auth/delete-user-internal",
        headers={
            "Authorization": f"Bearer {admin_token}",
            "Language": "es"
        },
        json={
            "user_id": str(user_to_delete)
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["notification_type"] == "success"
    assert data["response"] is None

@pytest.mark.asyncio
async def test_delete_user_internal_forbidden_non_admin(client: TestClient, user_token):
    """Test que usuario sin rol ADMIN no puede acceder"""
    response = client.delete(
        "/auth/delete-user-internal",
        headers={
            "Authorization": f"Bearer {user_token}",
            "Language": "es"
        },
        json={
            "user_id": "550e8400-e29b-41d4-a716-446655440000"
        }
    )
    
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_delete_user_internal_invalid_uuid(client: TestClient, admin_token):
    """Test validación Pydantic de UUID"""
    response = client.delete(
        "/auth/delete-user-internal",
        headers={
            "Authorization": f"Bearer {admin_token}",
            "Language": "es"
        },
        json={
            "user_id": "invalid-uuid"
        }
    )
    
    assert response.status_code == 422
```

**Escenarios de Integration Tests:**

- ✅ Probar flujo completo con base de datos real
- ✅ Validar que se eliminan todos los registros:
  - N registros en `user_location_rol`
  - 1 registro en `user`
  - 1 registro en `platform`
- ✅ Probar escenario de usuario con múltiples ubicaciones
- ✅ Validar restricción de rol ADMIN
- ✅ Validar permisos DELETE
- ✅ Validar response con `response: null`
- ✅ Validar que no puede auto-eliminarse
- ✅ Validar mensaje de relaciones activas (cuando se implemente)

---

## Referencias

- **[07-01] Create User Internal Flow**: Flujo de creación (este es el inverso)
- **[03-00] Business Flow Overview**: Patrón de Business Flow
- **[02-00] Entity Flow Overview**: Use Cases de entidades utilizados
- **[05-02] Database Entities**: Entidades de base de datos involucradas

---

## Historial de Cambios

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0 | Dic 2024 | Creación inicial de especificación. Flujo inverso al de creación de usuario interno. Incluye validación de relaciones activas, eliminación atómica de user_location_rol, user y platform. Restricción a rol ADMIN con permiso DELETE. | Equipo de Desarrollo Goluti |

---

**Fin del Documento**


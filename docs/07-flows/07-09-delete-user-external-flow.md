# Flujo de Eliminación de Usuario Externo (Delete User External)

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

El flujo de **Delete User External** permite la eliminación completa de usuarios externos del sistema, aplicando el flujo inverso al de creación. Este endpoint elimina de manera atómica las entidades relacionadas que fueron creadas durante el proceso de alta del usuario externo.

Este flujo está basado en el proceso inverso de [Create User External](./07-02-create-user-external-flow.md).

**Diferencia con Delete User Internal**: Los usuarios externos NO tienen registros en `user_location_rol` (no tienen roles ni ubicaciones asignadas), por lo que el flujo es más simple.

---

## Objetivo

Proporcionar un endpoint único que permita eliminar un usuario externo completo del sistema, ejecutando las siguientes operaciones de manera atómica (flujo inverso a la creación):

1. Validar que el usuario existe y puede ser eliminado
2. Verificar que el usuario no tiene relaciones activas adicionales
3. Eliminar el registro del `user`
4. Eliminar el registro de `platform` asociado

### Alcance

**En alcance:**
- Eliminación del registro `user`
- Eliminación de la configuración de `platform` asociada
- Validación de relaciones activas que impidan la eliminación
- Validaciones de integridad referencial
- Transaccionalidad del proceso completo (rollback si falla algún paso)

**Fuera de alcance:**
- Eliminación de datos históricos o logs del usuario
- Notificación por email de eliminación
- Soft delete (se realiza hard delete)
- Eliminación de usuarios internos (flujo separado en [07-08](./07-08-delete-user-internal-flow.md))

---

## Contexto de Negocio

### Problema que Resuelve

Actualmente, eliminar un usuario externo requiere múltiples llamadas a diferentes endpoints en orden específico:
1. `DELETE /user` - Eliminar usuario
2. `DELETE /platform` - Eliminar configuración de plataforma

Este flujo unifica todo en una sola operación atómica, garantizando consistencia y simplificando el proceso.

**Nota**: A diferencia de usuarios internos, los usuarios externos NO tienen registros en `user_location_rol` porque no tienen roles ni ubicaciones asignadas (su `platform.location_id` es `null`).

### Beneficios Esperados

- ✅ Simplificación del proceso de baja de usuarios externos
- ✅ Garantía de atomicidad (todo o nada)
- ✅ Reducción de errores por proceso manual
- ✅ Validaciones centralizadas de relaciones activas
- ✅ Prevención de eliminación de usuarios con flujos activos
- ✅ Limpieza completa de datos relacionados

---

## Actores Involucrados

| Actor | Rol | Responsabilidad |
|-------|-----|-----------------|
| **Usuario Externo** | User del sistema | Eliminar su propia cuenta (self-delete) |
| **Sistema** | Automático | Validar datos, eliminar registros, verificar relaciones |

---

## Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────────┐
│              Request DELETE /auth/delete-user-external/{user_id}│
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
│                    3. ELIMINAR USUARIO                           │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ UserDeleteUseCase.execute({                               │  │
│  │   id: user_id                                             │  │
│  │ })                                                         │  │
│  │                                                            │  │
│  │ Guarda platform_id antes de eliminar para paso 4          │  │
│  │                                                            │  │
│  │ Si falla → ROLLBACK completo                              │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    4. ELIMINAR PLATFORM                          │
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
│              5. RETORNAR MENSAJE DE ÉXITO                        │
│  {                                                               │
│    message_type: "temporary",                                    │
│    notification_type: "success",                                 │
│    message: "Usuario externo eliminado exitosamente",           │
│    response: { message: "..." }                                  │
│  }                                                               │
│                                                                  │
│  Nota: El mensaje es traducido usando KEYS_MESSAGES              │
│        según el idioma configurado en el header                  │
└─────────────────────────────────────────────────────────────────┘
```

### Comparación: Flujo Creación vs Eliminación

| Paso | Creación | Eliminación (Inverso) |
|------|----------|----------------------|
| 1 | Validar language, currency | Validar que usuario existe |
| 2 | Validar email único | Verificar relaciones activas |
| 3 | Validar identification único | Eliminar User |
| 4 | Crear Platform (location_id=null) | Eliminar Platform |
| 5 | Crear User | Retornar éxito |
| 6 | Retornar éxito | - |

### Estados del Flujo

| Estado | Descripción | Siguiente Estado |
|--------|-------------|-----------------|
| **VALIDATING_USER** | Validando que usuario existe | CHECKING_RELATIONS, ERROR |
| **CHECKING_RELATIONS** | Verificando relaciones activas | DELETING_USER, ERROR |
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
│  │  DELETE /auth/delete-user-external/{user_id}           │  │
│  │  - AuthRouter                                          │  │
│  │  - @check_permissions([PERMISSION_TYPE.DELETE])        │  │
│  │  - @check_roles([ROL_TYPE.ADMIN])                      │  │
│  │  - @execute_transaction_route                          │  │
│  └──────────────────────┬─────────────────────────────────┘  │
└─────────────────────────┼────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│         Infrastructure/Web/Controller Layer                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  AuthController.delete_user_external()                 │  │
│  │  - Invoca Use Case                                     │  │
│  │  - Construye Response                                  │  │
│  └──────────────────────┬─────────────────────────────────┘  │
└─────────────────────────┼────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│              Domain/Business Use Case Layer                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  DeleteUserExternalUseCase.execute()                   │  │
│  │  ├─ 1. UserReadUseCase (validar existencia)            │  │
│  │  │                                                      │  │
│  │  ├─ 2. Verificar relaciones activas                    │  │
│  │  │    └─ [Consultas a otras tablas si aplica]          │  │
│  │  │                                                      │  │
│  │  ├─ 3. UserDeleteUseCase                               │  │
│  │  │                                                      │  │
│  │  └─ 4. PlatformDeleteUseCase                           │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### Componentes Principales

#### 1. Models (`src/domain/models/business/auth/delete_user_external/`)

**Archivos a crear:**
- `delete_user_external_request.py`
- `delete_user_external_response.py`
- `index.py`
- `__init__.py`

#### 2. Use Case (`src/domain/services/use_cases/business/auth/delete_user_external/`)

**Archivos a crear:**
- `delete_user_external_use_case.py`
- `__init__.py`

#### 3. Controller (actualizar existente)

**Archivo a actualizar:**
- `src/infrastructure/web/controller/business/auth_controller.py`

#### 4. Router (actualizar existente)

**Archivo a actualizar:**
- `src/infrastructure/web/business_routes/auth_router.py`

---

## Endpoints API

### Endpoint: Delete User External

```
DELETE /auth/delete-user-external/{user_id}
```

**Headers:**
```
Authorization: Bearer <token>
Language: es | en
```

**Restricciones de Acceso:**
- ⚠️ **Rol requerido**: `USER` (solo usuarios externos)
- **Permiso requerido**: `PERMISSION_TYPE.DELETE`
- **Autenticación**: Token JWT válido
- **Self-delete obligatorio**: El usuario solo puede eliminar **su propia cuenta**

**Path Parameters:**
| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `user_id` | UUID | Sí | ID del usuario externo a eliminar |

**Ejemplo de URL:**
```
DELETE /auth/delete-user-external/550e8400-e29b-41d4-a716-446655440000
```

**Response (Success - 200 OK):**
```json
{
  "message_type": "temporary",
  "notification_type": "success",
  "message": "Usuario externo eliminado exitosamente",
  "response": {
    "message": "Usuario externo eliminado exitosamente"
  }
}
```

**Response (Error - Usuario No Encontrado):**
```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "El usuario con ID 550e8400-e29b-41d4-a716-446655440000 no existe en el sistema",
  "response": null
}
```

**Response (Error - Usuario con Relaciones Activas):**
```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "El usuario está relacionado a flujos activos y no puede ser eliminado",
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

**Archivo**: `src/domain/models/business/auth/delete_user_external/delete_user_external_request.py`

```python
from pydantic import BaseModel, Field, UUID4


class DeleteUserExternalRequest(BaseModel):
    user_id: UUID4 = Field(..., description="ID del usuario externo a eliminar")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }
```

### Response Model

**Archivo**: `src/domain/models/business/auth/delete_user_external/delete_user_external_response.py`

```python
from pydantic import BaseModel, Field


class DeleteUserExternalResponse(BaseModel):
    message: str = Field(...)
```

### Index File

**Archivo**: `src/domain/models/business/auth/delete_user_external/index.py`

```python
from .delete_user_external_request import DeleteUserExternalRequest
from .delete_user_external_response import DeleteUserExternalResponse

__all__ = [
    "DeleteUserExternalRequest",
    "DeleteUserExternalResponse"
]
```

---

## Validaciones y Reglas

### Reglas de Negocio

1. **Usuario Existe**: El `user_id` debe existir en la tabla `user`
2. **Self-Delete Obligatorio**: El `user_id` debe coincidir con el usuario autenticado (`user_id` == `config.token.user_id`)
3. **Sin Relaciones Activas**: El usuario no debe tener relaciones activas en otras tablas del sistema
4. **Eliminación Completa**: Se eliminan los registros de `user` y `platform`
5. **Atomicidad**: Si falla algún paso de eliminación, se debe hacer rollback de toda la operación
6. **Solo Usuarios Externos**: Este endpoint está diseñado para usuarios externos con rol USER

### Nuevas Claves de Traducción Requeridas

**Archivo**: `src/core/enums/keys_message.py`

Agregar las siguientes claves al enum `KEYS_MESSAGES`:

```python
AUTH_DELETE_USER_EXTERNAL_NOT_FOUND = "auth_delete_user_external_not_found"
AUTH_DELETE_USER_EXTERNAL_HAS_ACTIVE_RELATIONS = "auth_delete_user_external_has_active_relations"
AUTH_DELETE_USER_EXTERNAL_UNAUTHORIZED = "auth_delete_user_external_unauthorized"
AUTH_DELETE_USER_EXTERNAL_SUCCESS = "auth_delete_user_external_success"
AUTH_DELETE_USER_EXTERNAL_ERROR_DELETING_USER = "auth_delete_user_external_error_deleting_user"
AUTH_DELETE_USER_EXTERNAL_ERROR_DELETING_PLATFORM = "auth_delete_user_external_error_deleting_platform"
```

**Traducciones necesarias en la tabla `translation`:**

| Key | Context | ES (Español) | EN (English) |
|-----|---------|--------------|--------------|
| `auth_delete_user_external_not_found` | backend | El usuario con ID {user_id} no existe en el sistema | The user with ID {user_id} does not exist in the system |
| `auth_delete_user_external_has_active_relations` | backend | El usuario está relacionado a flujos activos y no puede ser eliminado | The user is related to active flows and cannot be deleted |
| `auth_delete_user_external_soft_deleted` | backend | Tu cuenta tiene relaciones activas y no pudo ser eliminada, pero fue inactivada. Será eliminada permanentemente después de 1 mes | Your account has active relations and could not be deleted, but was deactivated. It will be permanently deleted after 1 month |
| `auth_delete_user_external_error_soft_delete` | backend | Error al inactivar tu cuenta | Error deactivating your account |
| `auth_delete_user_external_unauthorized` | backend | No tiene autorización para eliminar este usuario | You are not authorized to delete this user |
| `auth_delete_user_external_success` | backend | Usuario externo eliminado exitosamente | External user deleted successfully |
| `auth_delete_user_external_error_deleting_user` | backend | Error al eliminar el usuario | Error deleting user |
| `auth_delete_user_external_error_deleting_platform` | backend | Error al eliminar la configuración de plataforma | Error deleting platform configuration |

### Migración SQL

**Archivo**: `migrations/changelog-v32.sql`

```sql
-- liquibase formatted sql
-- changeset delete-user-external-translations:1733443200000-32

-- ============================================
-- Traducciones para flujo Delete User External
-- ============================================

-- Errores de validación
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'auth_delete_user_external_not_found', 'es', 'El usuario con ID {user_id} no existe en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_external_not_found', 'en', 'The user with ID {user_id} does not exist in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_delete_user_external_has_active_relations', 'es', 'El usuario está relacionado a flujos activos y no puede ser eliminado', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_external_has_active_relations', 'en', 'The user is related to active flows and cannot be deleted', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_delete_user_external_unauthorized', 'es', 'No tiene autorización para eliminar este usuario', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_external_unauthorized', 'en', 'You are not authorized to delete this user', 'backend', true, now(), now());

-- Errores de proceso
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'auth_delete_user_external_error_deleting_user', 'es', 'Error al eliminar el usuario', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_external_error_deleting_user', 'en', 'Error deleting user', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_delete_user_external_error_deleting_platform', 'es', 'Error al eliminar la configuración de plataforma', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_external_error_deleting_platform', 'en', 'Error deleting platform configuration', 'backend', true, now(), now());

-- Éxito
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'auth_delete_user_external_success', 'es', 'Usuario externo eliminado exitosamente', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_external_success', 'en', 'External user deleted successfully', 'backend', true, now(), now());

--ROLLBACK DELETE FROM translation WHERE "key" LIKE 'auth_delete_user_external_%';
```

---

## Casos de Uso Involucrados

### Use Cases de Validación (Read)

| Use Case | Propósito | Cantidad de Ejecuciones |
|----------|-----------|-------------------------|
| `UserReadUseCase` | Validar que user_id existe y obtener platform_id | 1 vez |

### Use Cases de Eliminación (Delete)

| Use Case | Propósito | Cantidad de Ejecuciones |
|----------|-----------|-------------------------|
| `UserDeleteUseCase` | Eliminar el registro de usuario | 1 vez |
| `PlatformDeleteUseCase` | Eliminar configuración de plataforma | 1 vez |

**Nota**: A diferencia de Delete User Internal, aquí NO se elimina `user_location_rol` porque los usuarios externos no tienen roles asignados.

---

## Use Case Principal

**Archivo**: `src/domain/services/use_cases/business/auth/delete_user_external/delete_user_external_use_case.py`

```python
from typing import Union
from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.wrappers.execute_transaction import execute_transaction
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity

from src.domain.models.business.auth.delete_user_external import (
    DeleteUserExternalRequest
)
from src.domain.models.entities.user.index import UserRead, UserDelete
from src.domain.models.entities.platform.index import PlatformDelete

from src.domain.services.use_cases.entities.user.user_read_use_case import (
    UserReadUseCase
)
from src.domain.services.use_cases.entities.user.user_delete_use_case import (
    UserDeleteUseCase
)
from src.domain.services.use_cases.entities.platform.platform_delete_use_case import (
    PlatformDeleteUseCase
)

from src.infrastructure.database.repositories.entities.user_repository import (
    UserRepository
)
from src.infrastructure.database.repositories.entities.platform_repository import (
    PlatformRepository
)


user_repository = UserRepository()
platform_repository = PlatformRepository()


class DeleteUserExternalUseCase:
    def __init__(self):
        self.user_read_uc = UserReadUseCase(user_repository)
        self.user_delete_uc = UserDeleteUseCase(user_repository)
        self.platform_delete_uc = PlatformDeleteUseCase(platform_repository)

        self.message = Message()

    async def _check_active_relations(
        self,
        config: Config,
        user_id: UUID4
    ) -> bool:
        return False

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: DeleteUserExternalRequest,
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
                    key=KEYS_MESSAGES.AUTH_DELETE_USER_EXTERNAL_NOT_FOUND.value,
                    params={"user_id": str(params.user_id)}
                ),
            )

        platform_id = user.platform_id

        has_active_relations = await self._check_active_relations(
            config=config,
            user_id=params.user_id
        )
        if has_active_relations:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_DELETE_USER_EXTERNAL_HAS_ACTIVE_RELATIONS.value
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
                    key=KEYS_MESSAGES.AUTH_DELETE_USER_EXTERNAL_ERROR_DELETING_USER.value
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
                    key=KEYS_MESSAGES.AUTH_DELETE_USER_EXTERNAL_ERROR_DELETING_PLATFORM.value
                ),
            )

        return None
```

---

### Router

**Archivo**: `src/infrastructure/web/business_routes/auth_router.py`

Agregar el endpoint al router existente:

```python
@auth_router.delete(
    "/delete-user-external/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=Response[DeleteUserExternalResponse]
)
@check_permissions([PERMISSION_TYPE.DELETE.value])
@check_roles([ROL_TYPE.USER.value])
@execute_transaction_route(enabled=settings.has_track)
async def delete_user_external(
    user_id: UUID = Path(..., description="ID del usuario externo a eliminar"),
    config: Config = Depends(get_config)
) -> Response[DeleteUserExternalResponse]:
    return await auth_controller.delete_user_external(config=config, user_id=user_id)
```

**Nota**: La validación de self-delete (que el usuario solo pueda eliminar su propia cuenta) se realiza en el Use Case.

---

## Manejo de Errores

| Error | Código HTTP | Mensaje | Solución |
|-------|-------------|---------|----------|
| Usuario no existe | 200 | "El usuario con ID {id} no existe en el sistema" | Verificar user_id |
| No autorizado (self-delete) | 200 | "No tiene autorización para eliminar este usuario" | Solo puede eliminar su propia cuenta |
| Relaciones activas | 200 | "El usuario está relacionado a flujos activos y no puede ser eliminado" | Resolver relaciones pendientes |
| Error eliminando user | 200 | "Error al eliminar el usuario" | Revisar logs |
| Error eliminando platform | 200 | "Error al eliminar la configuración de plataforma" | Revisar logs |
| Rol no autorizado | 403 | "No tiene permisos de rol" | Debe tener rol USER |
| Sin permisos | 403 | "No tiene permisos para realizar esta acción" | Debe tener permiso DELETE |
| Token inválido | 401 | "Token inválido o expirado" | Renovar token |

---

## Seguridad

### Permisos Requeridos

```python
@check_permissions([PERMISSION_TYPE.DELETE.value])
@check_roles([ROL_TYPE.USER.value])
```

**Restricción de Rol:**
- ⚠️ **Solo rol USER**: Solo usuarios externos pueden usar este endpoint
- **Self-delete obligatorio**: El usuario solo puede eliminar su propia cuenta
- El rol debe estar activo y vigente
- El usuario debe tener el permiso `DELETE` asociado a su rol

### Validaciones de Seguridad

1. **Validación de Rol**: Solo `USER` puede acceder al endpoint
2. **Validación de Self-Delete**: Se valida que `user_id == config.token.user_id`
3. **Validación de Permiso**: Requiere permiso `DELETE`
4. **Token JWT**: Validación en cada request
5. **Auditoría**: El decorador `@execute_transaction` registra la operación

### Lógica de Autorización en Use Case

```python
# Solo puede eliminar su propia cuenta (self-delete)
if str(params.user_id) != str(config.token.user_id):
    return await self.message.get_message(
        config=config,
        message=MessageCoreEntity(
            key=KEYS_MESSAGES.AUTH_DELETE_USER_EXTERNAL_UNAUTHORIZED.value
        ),
    )
```

---

## Ejemplos de Uso

### Caso de Uso 1: Eliminar Usuario Exitosamente

**Request:**
```bash
curl -X DELETE "https://api.goluti.com/auth/delete-user-external/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer TOKEN" \
  -H "Language: es"
```

**Response:**
```json
{
  "message_type": "temporary",
  "notification_type": "success",
  "message": "Usuario externo eliminado exitosamente",
  "response": {
    "message": "Usuario externo eliminado exitosamente"
  }
}
```

### Caso de Uso 2: Error - Intento de Eliminar Otro Usuario

**Escenario**: Un usuario intenta eliminar otro usuario (no permitido, solo self-delete).

**Request:**
```bash
curl -X DELETE "https://api.goluti.com/auth/delete-user-external/OTRO_USER_ID" \
  -H "Authorization: Bearer TOKEN_USER" \
  -H "Language: es"
```

**Response:**
```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "No tiene autorización para eliminar este usuario",
  "response": null
}
```

### Caso de Uso 3: Error - Usuario No Encontrado

**Request:**
```bash
curl -X DELETE "https://api.goluti.com/auth/delete-user-external/999e8400-e29b-41d4-a716-446655440000" \
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

---

## Referencias

- **[07-02] Create User External Flow**: Flujo de creación (este es el inverso)
- **[07-08] Delete User Internal Flow**: Flujo de eliminación de usuarios internos
- **[03-00] Business Flow Overview**: Patrón de Business Flow
- **[05-02] Database Entities**: Entidades de base de datos involucradas

---

## Historial de Cambios

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0 | Dic 2024 | Creación inicial de especificación. Flujo inverso al de creación de usuario externo. Eliminación atómica de user y platform. Restricción a rol ADMIN con permiso DELETE. | Equipo de Desarrollo Goluti |

---

**Fin del Documento**


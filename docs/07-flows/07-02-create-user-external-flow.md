# Especificación de Flujo: Create User External

**Documento:** 07-02-create-user-external-flow.md  
**Versión:** 1.0  
**Fecha:** Noviembre 10, 2024  
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
8. [Validaciones y Reglas de Negocio](#validaciones-y-reglas-de-negocio)
9. [Nuevas Claves de Traducción Requeridas](#nuevas-claves-de-traducción-requeridas)
10. [Casos de Uso Involucrados](#casos-de-uso-involucrados)
11. [Implementación Detallada](#implementación-detallada)
12. [Manejo de Errores](#manejo-de-errores)
13. [Seguridad](#seguridad)
14. [Ejemplos de Uso](#ejemplos-de-uso)
15. [Testing](#testing)
16. [Consideraciones Técnicas](#consideraciones-técnicas)
17. [Historial de Cambios](#historial-de-cambios)

---

## Resumen Ejecutivo

Este documento especifica el flujo de negocio para la creación de **usuarios externos** en el sistema Goluti Backend Platform. Los usuarios externos son aquellos que acceden al sistema sin estar vinculados a ubicaciones ni roles específicos de la empresa (por ejemplo: clientes, usuarios públicos).

**Características principales:**
- ✅ Creación simplificada de usuarios sin roles corporativos
- ✅ Platform sin ubicación asociada (`location_id = null`)
- ✅ Validación de unicidad de email e identification
- ✅ Configuración personalizada de expiración de tokens
- ✅ Sistema de traducciones integrado
- ✅ Endpoint público (sin restricciones de rol)

---

## Objetivo del Flujo

Permitir la creación de usuarios externos en el sistema de manera simple y eficiente, sin necesidad de asignarles roles corporativos o ubicaciones específicas.

### Alcance

**En alcance:**
- ✅ Creación de registro en tabla `platform` con `location_id = null`
- ✅ Creación de registro en tabla `user` vinculado al platform
- ✅ Validación de unicidad de email
- ✅ Validación de unicidad de identification
- ✅ Validación de existencia de `language_id` y `currency_id`
- ✅ Hash automático de contraseña
- ✅ Configuración de tiempos de expiración de tokens
- ✅ Uso del sistema de traducciones del proyecto

**Fuera de alcance:**
- ❌ Asignación de roles o permisos
- ❌ Vinculación con ubicaciones (locations)
- ❌ Creación de registros en `user_location_rol`
- ❌ Verificación de email (se implementará en flujo separado)
- ❌ Onboarding o procesos adicionales

---

## Contexto de Negocio

### Problema

El sistema requiere la capacidad de registrar usuarios externos (clientes, usuarios públicos) que no forman parte de la estructura organizacional de la empresa. Estos usuarios necesitan acceso al sistema pero sin roles corporativos ni ubicaciones asignadas.

### Solución

Crear un endpoint dedicado `/auth/create-user-external` que:
1. Crea una configuración de platform básica sin ubicación
2. Registra al usuario en el sistema
3. Valida la unicidad de credenciales (email, identification)
4. Genera un registro limpio y simple para usuarios públicos

### Beneficios

- ✅ **Simplicidad**: No requiere información corporativa compleja
- ✅ **Flexibilidad**: Platform sin ubicación permite uso global
- ✅ **Escalabilidad**: Fácil de integrar con flujos de registro público
- ✅ **Seguridad**: Validaciones estrictas de unicidad

---

## Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────────┐
│                   INICIO: Create User External                  │
│                 POST /auth/create-user-external                 │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│           1. VALIDAR DATOS DE ENTRADA (Pydantic)                │
│  - language_id: UUID requerido                                  │
│  - currency_id: UUID requerido                                  │
│  - email: EmailStr válido                                       │
│  - password: min 8 caracteres                                   │
│  - identification: min 3 caracteres                             │
│  - first_name, last_name: min 2 caracteres                      │
│  - phone: opcional, max 20 caracteres                           │
│  - token_expiration_minutes: opcional (default 60)              │
│  - refresh_token_expiration_minutes: opcional (default 1440)    │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              2. VALIDAR LANGUAGE_ID EXISTE                      │
│  LanguageReadUseCase.execute(language_id)                       │
│  ├─ Si no existe → Error: "El idioma especificado no existe"   │
│  └─ Si existe → Continuar                                       │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              3. VALIDAR CURRENCY_ID EXISTE                      │
│  CurrencyReadUseCase.execute(currency_id)                       │
│  ├─ Si no existe → Error: "La moneda especificada no existe"   │
│  └─ Si existe → Continuar                                       │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              4. VALIDAR EMAIL ES ÚNICO                          │
│  UserListUseCase.execute(filters=[email == request.email])      │
│  ├─ Si existe → Error: "El email ya está registrado"           │
│  └─ Si no existe → Continuar                                    │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              5. VALIDAR IDENTIFICATION ES ÚNICO                 │
│  UserListUseCase.execute(                                       │
│    filters=[identification == request.identification]           │
│  )                                                              │
│  ├─ Si existe → Error: "La identificación ya está registrada"  │
│  └─ Si no existe → Continuar                                    │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              6. CREAR PLATFORM (location_id = null)             │
│  PlatformSaveUseCase.execute(                                   │
│    language_id=request.language_id,                             │
│    location_id=None,  ← SIN UBICACIÓN                           │
│    currency_id=request.currency_id,                             │
│    token_expiration_minutes=request.token_expiration_minutes,   │
│    refresh_token_expiration_minutes=...                         │
│  )                                                              │
│  ├─ Error → Error: "Error al crear la configuración"           │
│  └─ Éxito → platform_created (con platform_id)                  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              7. CREAR USER (con hash de password)               │
│  UserSaveUseCase.execute(                                       │
│    platform_id=platform_created.id,                             │
│    email=request.email,                                         │
│    password=request.password,  ← Se hashea automáticamente      │
│    identification=request.identification,                       │
│    first_name=request.first_name,                               │
│    last_name=request.last_name,                                 │
│    phone=request.phone,                                         │
│    state=True                                                   │
│  )                                                              │
│  ├─ Error → Error: "Error al crear el usuario"                 │
│  └─ Éxito → user_created                                        │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              8. RETORNAR MENSAJE DE ÉXITO                        │
│  {                                                               │
│    message_type: "temporary",                                    │
│    notification_type: "success",                                 │
│    message: "Usuario externo creado exitosamente",              │
│    response: null                                                │
│  }                                                               │
│                                                                  │
│  Nota: El mensaje es traducido usando KEYS_MESSAGES              │
│        según el idioma configurado en el header                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Componentes Involucrados

### Archivos a Crear/Modificar

#### 1. Modelos de Request

**Archivos a crear:**
- `src/domain/models/business/auth/create_user_external/create_user_external_request.py`
- `src/domain/models/business/auth/create_user_external/__init__.py`

#### 2. Use Case Principal

**Archivo a crear:**
- `src/domain/services/use_cases/business/auth/create_user_external/create_user_external_use_case.py`
- `src/domain/services/use_cases/business/auth/create_user_external/__init__.py`

#### 3. Controller (actualizar existente)

**Archivo a actualizar:**
- `src/infrastructure/web/controller/business/auth_controller.py`

#### 4. Router (actualizar existente)

**Archivo a actualizar:**
- `src/infrastructure/web/business_routes/auth_router.py`

---

## Endpoints API

### Endpoint: Create User External

```
POST /auth/create-user-external
```

**Descripción**: Crea un usuario externo (público) sin roles ni ubicaciones asignadas.

**Headers Requeridos:**
```
Content-Type: application/json
Language: es | en
```

**Restricciones de Acceso:**
- **Público**: No requiere autenticación
- **Rate Limiting**: Aplicable según configuración del sistema

**Request Body:**

```json
{
  "language_id": "550e8400-e29b-41d4-a716-446655440000",
  "currency_id": "770e8400-e29b-41d4-a716-446655440000",
  "email": "usuario@example.com",
  "password": "SecurePassword123!",
  "identification": "12345678",
  "first_name": "Juan",
  "last_name": "Pérez",
  "phone": "+573001234567",
  "token_expiration_minutes": 60,
  "refresh_token_expiration_minutes": 1440
}
```

**Notas sobre Request:**
- `phone` es opcional
- `token_expiration_minutes` y `refresh_token_expiration_minutes` son opcionales con valores por defecto

**Response (Success - 200 OK):**
```json
{
  "message_type": "temporary",
  "notification_type": "success",
  "message": "Usuario externo creado exitosamente",
  "response": null
}
```

**Nota:** El campo `response` es `null` para este endpoint. El mensaje de éxito se obtiene del sistema de traducción usando `KEYS_MESSAGES.AUTH_CREATE_USER_EXTERNAL_SUCCESS`.

**Response (Error - Validación):**
```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "El email ya está registrado en el sistema",
  "response": null
}
```

**Response (Error - Language No Existe):**
```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "El idioma especificado no existe en el sistema",
  "response": null
}
```

**Response (Error - Currency No Existe):**
```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "La moneda especificada no existe en el sistema",
  "response": null
}
```

**Response (Error - Identification Duplicado):**
```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "La identificación ya está registrada en el sistema",
  "response": null
}
```

---

## Modelos de Datos

### Request Model

**Archivo**: `src/domain/models/business/auth/create_user_external/create_user_external_request.py`

```python
from pydantic import BaseModel, EmailStr, Field, UUID4
from typing import Optional


class CreateUserExternalRequest(BaseModel):
    language_id: UUID4 = Field(..., description="ID del idioma del usuario")
    currency_id: UUID4 = Field(..., description="ID de la moneda")
    email: EmailStr = Field(..., description="Email único del usuario")
    password: str = Field(..., min_length=8, max_length=255, description="Contraseña (será hasheada)")
    identification: str = Field(..., min_length=3, max_length=30, description="Documento de identificación único")
    first_name: str = Field(..., min_length=2, max_length=100, description="Primer nombre")
    last_name: str = Field(..., min_length=2, max_length=100, description="Apellido")
    phone: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto")
    token_expiration_minutes: Optional[int] = Field(default=60, ge=5, le=1440, description="Minutos de expiración del token")
    refresh_token_expiration_minutes: Optional[int] = Field(default=1440, ge=60, le=43200, description="Minutos de expiración del refresh token")

    class Config:
        json_schema_extra = {
            "example": {
                "language_id": "550e8400-e29b-41d4-a716-446655440000",
                "currency_id": "770e8400-e29b-41d4-a716-446655440000",
                "email": "usuario@example.com",
                "password": "SecurePassword123!",
                "identification": "12345678",
                "first_name": "Juan",
                "last_name": "Pérez",
                "phone": "+573001234567",
                "token_expiration_minutes": 60,
                "refresh_token_expiration_minutes": 1440
            }
        }
```

### Index File

**Archivo**: `src/domain/models/business/auth/create_user_external/__init__.py`

```python
from .create_user_external_request import CreateUserExternalRequest

__all__ = [
    "CreateUserExternalRequest"
]
```

---

## Validaciones y Reglas de Negocio

### Validaciones de Entrada (Pydantic)

| Campo | Regla | Mensaje de Error |
|-------|-------|------------------|
| `language_id` | UUID válido, requerido | "Campo requerido" |
| `currency_id` | UUID válido, requerido | "Campo requerido" |
| `email` | EmailStr válido, requerido | "Email inválido" |
| `password` | Min 8, max 255 caracteres | "La contraseña debe tener entre 8 y 255 caracteres" |
| `identification` | Min 3, max 30 caracteres | "La identificación debe tener entre 3 y 30 caracteres" |
| `first_name` | Min 2, max 100 caracteres | "El nombre debe tener entre 2 y 100 caracteres" |
| `last_name` | Min 2, max 100 caracteres | "El apellido debe tener entre 2 y 100 caracteres" |
| `phone` | Opcional, max 20 caracteres | "El teléfono no debe exceder 20 caracteres" |
| `token_expiration_minutes` | Entre 5 y 1440 (24h) | "Debe estar entre 5 y 1440 minutos" |
| `refresh_token_expiration_minutes` | Entre 60 y 43200 (30 días) | "Debe estar entre 60 y 43200 minutos" |

### Validaciones de Use Case

| Validación | Descripción | Mensaje de Error (Key) |
|------------|-------------|------------------------|
| Language existe | Verificar que `language_id` existe en BD | `AUTH_CREATE_USER_EXTERNAL_LANGUAGE_NOT_FOUND` |
| Currency existe | Verificar que `currency_id` existe en BD | `AUTH_CREATE_USER_EXTERNAL_CURRENCY_NOT_FOUND` |
| Email único | Verificar que no existe otro user con ese email | `AUTH_CREATE_USER_EXTERNAL_EMAIL_ALREADY_EXISTS` |
| Identification único | Verificar que no existe otro user con esa identification | `AUTH_CREATE_USER_EXTERNAL_IDENTIFICATION_ALREADY_EXISTS` |

### Reglas de Negocio

1. **Platform sin Ubicación**: El `location_id` en platform debe ser `null` para usuarios externos
2. **Estado Inicial**: Los usuarios externos se crean con `state=True` (activos)
3. **Hash de Password**: La contraseña se hashea automáticamente en el use case `UserSaveUseCase`
4. **Sin Roles**: Los usuarios externos no tienen roles asignados al momento de creación
5. **Unicidad Estricta**: Tanto email como identification deben ser únicos en el sistema

---

## Nuevas Claves de Traducción Requeridas

Agregar las siguientes claves al enum `KEYS_MESSAGES`:

**Archivo**: `src/core/enums/keys_message.py`

```python
AUTH_CREATE_USER_EXTERNAL_LANGUAGE_NOT_FOUND = "auth_create_user_external_language_not_found"
AUTH_CREATE_USER_EXTERNAL_CURRENCY_NOT_FOUND = "auth_create_user_external_currency_not_found"
AUTH_CREATE_USER_EXTERNAL_EMAIL_ALREADY_EXISTS = "auth_create_user_external_email_already_exists"
AUTH_CREATE_USER_EXTERNAL_IDENTIFICATION_ALREADY_EXISTS = "auth_create_user_external_identification_already_exists"
AUTH_CREATE_USER_EXTERNAL_SUCCESS = "auth_create_user_external_success"
```

**Traducciones necesarias en la tabla `translation`:**

| Key | Context | ES (Español) | EN (English) |
|-----|---------|--------------|--------------|
| `auth_create_user_external_language_not_found` | backend | El idioma especificado no existe en el sistema | The specified language does not exist in the system |
| `auth_create_user_external_currency_not_found` | backend | La moneda especificada no existe en el sistema | The specified currency does not exist in the system |
| `auth_create_user_external_email_already_exists` | backend | El email ya está registrado en el sistema | The email is already registered in the system |
| `auth_create_user_external_identification_already_exists` | backend | La identificación ya está registrada en el sistema | The identification is already registered in the system |
| `auth_create_user_external_success` | backend | Usuario externo creado exitosamente | External user created successfully |

---

## Casos de Uso Involucrados

### Use Cases de Validación (Read)

| Use Case | Propósito | Cantidad de Ejecuciones |
|----------|-----------|-------------------------|
| `LanguageReadUseCase` | Validar que language_id existe | 1 vez |
| `CurrencyReadUseCase` | Validar que currency_id existe | 1 vez |
| `UserListUseCase` | Validar unicidad de email | 1 vez |
| `UserListUseCase` | Validar unicidad de identification | 1 vez |

**Total de validaciones por request**: 4

### Use Cases de Creación (Save)

| Use Case | Propósito | Cantidad de Ejecuciones |
|----------|-----------|-------------------------|
| `PlatformSaveUseCase` | Crear platform sin ubicación | 1 vez |
| `UserSaveUseCase` | Crear usuario externo | 1 vez |

**Total de creaciones por request**: 2

---

## Implementación Detallada

### Use Case Principal

**Archivo**: `src/domain/services/use_cases/business/auth/create_user_external/create_user_external_use_case.py`

```python
from typing import Union
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

from src.domain.models.business.auth.create_user_external import (
    CreateUserExternalRequest
)
from src.domain.models.entities.platform.index import PlatformSave
from src.domain.models.entities.user.index import UserSave
from src.domain.models.entities.language.index import LanguageRead
from src.domain.models.entities.currency.index import CurrencyRead

from src.domain.services.use_cases.entities.language.language_read_use_case import (
    LanguageReadUseCase
)
from src.domain.services.use_cases.entities.currency.currency_read_use_case import (
    CurrencyReadUseCase
)
from src.domain.services.use_cases.entities.user.user_list_use_case import (
    UserListUseCase
)
from src.domain.services.use_cases.entities.platform.platform_save_use_case import (
    PlatformSaveUseCase
)
from src.domain.services.use_cases.entities.user.user_save_use_case import (
    UserSaveUseCase
)

from src.infrastructure.database.repositories.entities.language_repository import (
    LanguageRepository
)
from src.infrastructure.database.repositories.entities.currency_repository import (
    CurrencyRepository
)
from src.infrastructure.database.repositories.entities.user_repository import (
    UserRepository
)
from src.infrastructure.database.repositories.entities.platform_repository import (
    PlatformRepository
)


language_repository = LanguageRepository()
currency_repository = CurrencyRepository()
user_repository = UserRepository()
platform_repository = PlatformRepository()


class CreateUserExternalUseCase:
    def __init__(self):
        self.language_read_uc = LanguageReadUseCase(language_repository)
        self.currency_read_uc = CurrencyReadUseCase(currency_repository)
        self.user_list_uc = UserListUseCase(user_repository)
        
        self.platform_save_uc = PlatformSaveUseCase(platform_repository)
        self.user_save_uc = UserSaveUseCase(user_repository)
        
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_B.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: CreateUserExternalRequest,
    ) -> Union[str, None]:
        config.response_type = RESPONSE_TYPE.OBJECT


        language = await self.language_read_uc.execute(
            config=config,
            params=LanguageRead(id=params.language_id)
        )
        if isinstance(language, str) or not language:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_CREATE_USER_EXTERNAL_LANGUAGE_NOT_FOUND.value
                ),
            )


        currency = await self.currency_read_uc.execute(
            config=config,
            params=CurrencyRead(id=params.currency_id)
        )
        if isinstance(currency, str) or not currency:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_CREATE_USER_EXTERNAL_CURRENCY_NOT_FOUND.value
                ),
            )


        existing_users_email = await self.user_list_uc.execute(
            config=config,
            params=Pagination(
                filters=[
                    FilterManager(
                        field="email",
                        condition=CONDITION_TYPE.EQUALS,
                        value=params.email
                    )
                ]
            )
        )
        if existing_users_email and not isinstance(existing_users_email, str):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_CREATE_USER_EXTERNAL_EMAIL_ALREADY_EXISTS.value
                ),
            )


        existing_users_identification = await self.user_list_uc.execute(
            config=config,
            params=Pagination(
                filters=[
                    FilterManager(
                        field="identification",
                        condition=CONDITION_TYPE.EQUALS,
                        value=params.identification
                    )
                ]
            )
        )
        if existing_users_identification and not isinstance(existing_users_identification, str):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_CREATE_USER_EXTERNAL_IDENTIFICATION_ALREADY_EXISTS.value
                ),
            )


        platform_created = await self.platform_save_uc.execute(
            config=config,
            params=PlatformSave(
                language_id=params.language_id,
                location_id=None,
                currency_id=params.currency_id,
                token_expiration_minutes=params.token_expiration_minutes,
                refresh_token_expiration_minutes=params.refresh_token_expiration_minutes
            )
        )

        if isinstance(platform_created, str) or not platform_created:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_ERROR_SAVING_RECORD.value
                ),
            )


        user_created = await self.user_save_uc.execute(
            config=config,
            params=UserSave(
                platform_id=platform_created.id,
                email=params.email,
                password=params.password,
                identification=params.identification,
                first_name=params.first_name,
                last_name=params.last_name,
                phone=params.phone,
                state=True
            )
        )

        if isinstance(user_created, str) or not user_created:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_ERROR_SAVING_RECORD.value
                ),
            )
        
        return None
```

**Archivo**: `src/domain/services/use_cases/business/auth/create_user_external/__init__.py`

```python
from .create_user_external_use_case import CreateUserExternalUseCase

__all__ = ["CreateUserExternalUseCase"]
```

---

### Controller

**Archivo**: `src/infrastructure/web/controller/business/auth_controller.py`

Agregar el método al controlador existente:

```python
@execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
async def create_user_external(
    self, 
    config: Config, 
    params: CreateUserExternalRequest
) -> Response[None]:
    result = await self.create_user_external_use_case.execute(
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
                key=KEYS_MESSAGES.AUTH_CREATE_USER_EXTERNAL_SUCCESS.value
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
@auth_router.post(
    "/create-user-external",
    status_code=status.HTTP_200_OK,
    response_model=Response[None]
)
@execute_transaction_route(enabled=settings.has_track)
async def create_user_external(
    params: CreateUserExternalRequest,
    config: Config = Depends(get_config_login)
) -> Response[None]:
    return await auth_controller.create_user_external(config=config, params=params)
```

**Nota**: Se usa `get_config_login` porque es un endpoint **público** (sin autenticación requerida).

---

## Manejo de Errores

| Error | Código HTTP | Mensaje | Solución |
|-------|-------------|---------|----------|
| Language no existe | 200 | "El idioma especificado no existe en el sistema" | Verificar language_id |
| Currency no existe | 200 | "La moneda especificada no existe en el sistema" | Verificar currency_id |
| Email duplicado | 200 | "El email ya está registrado en el sistema" | Usar otro email |
| Identification duplicado | 200 | "La identificación ya está registrada en el sistema" | Usar otra identificación |
| Error en Platform | 200 | "Error al guardar el registro" | Revisar logs |
| Error en User | 200 | "Error al guardar el registro" | Revisar logs |
| Validación Pydantic | 422 | Detalles de validación | Corregir formato de datos |

**Nota**: Los errores de negocio se retornan con código 200 y `notification_type: "error"` según el patrón del proyecto.

---

## Seguridad

### Autenticación

- ✅ **Endpoint Público**: No requiere autenticación (token JWT)
- ✅ **Rate Limiting**: Se aplica según configuración del middleware
- ✅ **CORS**: Configurado en middleware

### Validación de Datos

- ✅ **Pydantic**: Validación automática de tipos y formatos
- ✅ **Email**: Validación de formato EmailStr
- ✅ **Password**: Hash automático con bcrypt en `UserSaveUseCase`
- ✅ **SQL Injection**: Protección por SQLAlchemy ORM

### Unicidad de Credenciales

- ✅ **Email único**: Verificado antes de creación
- ✅ **Identification único**: Verificado antes de creación

### Consideraciones

1. **Sin Rate Limiting agresivo**: Permitir registro de múltiples usuarios
2. **Captcha recomendado**: Implementar en frontend para prevenir bots
3. **Verificación de email**: Implementar en flujo separado
4. **Password policy**: Validar complejidad en frontend

---

## Ejemplos de Uso

### Caso de Uso 1: Registro de Usuario Público Exitoso

**Request:**
```bash
curl -X POST https://api.goluti.com/auth/create-user-external \
  -H "Language: es" \
  -H "Content-Type: application/json" \
  -d '{
    "language_id": "550e8400-e29b-41d4-a716-446655440000",
    "currency_id": "770e8400-e29b-41d4-a716-446655440000",
    "email": "maria.garcia@gmail.com",
    "password": "MiPassword123!",
    "identification": "98765432",
    "first_name": "María",
    "last_name": "García",
    "phone": "+573009876543"
  }'
```

**Response:**
```json
{
  "message_type": "temporary",
  "notification_type": "success",
  "message": "Usuario externo creado exitosamente",
  "response": null
}
```

### Caso de Uso 2: Error - Email Duplicado

**Request:**
```bash
curl -X POST https://api.goluti.com/auth/create-user-external \
  -H "Language: en" \
  -H "Content-Type: application/json" \
  -d '{
    "language_id": "550e8400-e29b-41d4-a716-446655440000",
    "currency_id": "770e8400-e29b-41d4-a716-446655440000",
    "email": "maria.garcia@gmail.com",
    "password": "OtraPassword456!",
    "identification": "11111111",
    "first_name": "Otro",
    "last_name": "Usuario"
  }'
```

**Response:**
```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "The email is already registered in the system",
  "response": null
}
```

### Caso de Uso 3: Error - Identification Duplicado

**Request:**
```bash
curl -X POST https://api.goluti.com/auth/create-user-external \
  -H "Language: es" \
  -H "Content-Type: application/json" \
  -d '{
    "language_id": "550e8400-e29b-41d4-a716-446655440000",
    "currency_id": "770e8400-e29b-41d4-a716-446655440000",
    "email": "usuario.nuevo@gmail.com",
    "password": "Password789!",
    "identification": "98765432",
    "first_name": "Nuevo",
    "last_name": "Usuario"
  }'
```

**Response:**
```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "La identificación ya está registrada en el sistema",
  "response": null
}
```

### Caso de Uso 4: Error - Validación Pydantic

**Request:**
```bash
curl -X POST https://api.goluti.com/auth/create-user-external \
  -H "Language: es" \
  -H "Content-Type: application/json" \
  -d '{
    "language_id": "invalid-uuid",
    "currency_id": "770e8400-e29b-41d4-a716-446655440000",
    "email": "invalid-email",
    "password": "123",
    "identification": "12",
    "first_name": "A",
    "last_name": "B"
  }'
```

**Response:**
```json
{
  "detail": [
    {
      "type": "uuid_parsing",
      "loc": ["body", "language_id"],
      "msg": "Input should be a valid UUID",
      "input": "invalid-uuid"
    },
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "input": "invalid-email"
    }
  ]
}
```

---

## Testing

### Estructura de Tests (Espejo)

Siguiendo el patrón del proyecto donde `tests/` es espejo de `domain/` e `infrastructure/`:

**Tests Unitarios (Use Case):**
```
tests/domain/services/use_cases/business/auth/create_user_external/
└── test_create_user_external_use_case.py
```

**Tests de Integración (Router):**
```
tests/infrastructure/web/business_routes/
└── test_auth_router.py (agregar casos para create_user_external)
```

### Test Cases Unitarios

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.domain.services.use_cases.business.auth.create_user_external import CreateUserExternalUseCase
from src.domain.models.business.auth.create_user_external import CreateUserExternalRequest


@pytest.mark.asyncio
async def test_create_user_external_success():
    use_case = CreateUserExternalUseCase()
    
    config = MagicMock()
    config.language = "es"
    
    request = CreateUserExternalRequest(
        language_id="550e8400-e29b-41d4-a716-446655440000",
        currency_id="770e8400-e29b-41d4-a716-446655440000",
        email="test@example.com",
        password="SecurePass123!",
        identification="12345678",
        first_name="Test",
        last_name="User"
    )
    
    result = await use_case.execute(config=config, params=request)
    
    assert result is None


@pytest.mark.asyncio
async def test_create_user_external_email_exists():
    use_case = CreateUserExternalUseCase()
    
    config = MagicMock()
    config.language = "es"
    
    request = CreateUserExternalRequest(
        language_id="550e8400-e29b-41d4-a716-446655440000",
        currency_id="770e8400-e29b-41d4-a716-446655440000",
        email="existing@example.com",
        password="SecurePass123!",
        identification="12345678",
        first_name="Test",
        last_name="User"
    )
    
    result = await use_case.execute(config=config, params=request)
    
    assert isinstance(result, str)
    assert "email" in result.lower()


@pytest.mark.asyncio
async def test_create_user_external_identification_exists():
    use_case = CreateUserExternalUseCase()
    
    config = MagicMock()
    config.language = "es"
    
    request = CreateUserExternalRequest(
        language_id="550e8400-e29b-41d4-a716-446655440000",
        currency_id="770e8400-e29b-41d4-a716-446655440000",
        email="test@example.com",
        password="SecurePass123!",
        identification="87654321",
        first_name="Test",
        last_name="User"
    )
    
    result = await use_case.execute(config=config, params=request)
    
    assert isinstance(result, str)
    assert "identificación" in result.lower() or "identification" in result.lower()
```

### Test Cases de Integración

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_user_external_endpoint_success(client: AsyncClient):
    response = await client.post(
        "/auth/create-user-external",
        headers={"Language": "es"},
        json={
            "language_id": "550e8400-e29b-41d4-a716-446655440000",
            "currency_id": "770e8400-e29b-41d4-a716-446655440000",
            "email": f"test_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "identification": str(random.randint(10000000, 99999999)),
            "first_name": "Test",
            "last_name": "User"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["notification_type"] == "success"
    assert data["response"] is None


@pytest.mark.asyncio
async def test_create_user_external_endpoint_invalid_data(client: AsyncClient):
    response = await client.post(
        "/auth/create-user-external",
        headers={"Language": "es"},
        json={
            "language_id": "invalid-uuid",
            "currency_id": "770e8400-e29b-41d4-a716-446655440000",
            "email": "invalid-email",
            "password": "123",
            "identification": "12",
            "first_name": "A",
            "last_name": "B"
        }
    )
    
    assert response.status_code == 422
```

---

## Consideraciones Técnicas

### Performance

- **Validaciones en paralelo**: Las validaciones de language y currency podrían ejecutarse en paralelo
- **Índices requeridos**: `email` y `identification` deben tener índices únicos en la tabla `user`
- **Caching**: Considerar cachear los resultados de `LanguageReadUseCase` y `CurrencyReadUseCase`

### Escalabilidad

- **Rate Limiting**: Configurar límites apropiados para prevenir spam
- **Queue System**: Considerar usar cola para procesar registros en alto volumen
- **Email Verification**: Implementar verificación asíncrona en flujo separado

### Mantenibilidad

- **Logging**: Todos los errores se logean automáticamente por `@execute_transaction`
- **Monitoring**: Implementar métricas de registros exitosos/fallidos
- **Auditoría**: Los campos `created_date` y `updated_date` se gestionan automáticamente

### Mejoras Futuras

1. **Email Verification**: Enviar email de verificación después de registro
2. **Password Policy**: Validar complejidad de contraseña (mayúsculas, números, símbolos)
3. **Captcha Integration**: Integrar reCAPTCHA o similar
4. **Social Login**: Permitir registro vía Google, Facebook, etc.
5. **Welcome Email**: Enviar email de bienvenida automático
6. **Profile Completion**: Flujo para completar perfil después de registro

---

## Historial de Cambios

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0 | Nov 2024 | Creación inicial de especificación para create-user-external. Incluye validaciones de unicidad (email, identification), creación de platform sin ubicación, integración con sistema de traducciones, endpoint público sin autenticación, y documentación completa de estructura de tests. | Equipo de Desarrollo Goluti |

---

**Fin del Documento**


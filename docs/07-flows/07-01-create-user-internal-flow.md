# Flujo de Creación de Usuario Interno (Create User Internal)

**Versión**: 1.0  
**Fecha**: Noviembre 2024  
**Estado**: En Desarrollo  
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

El flujo de **Create User Internal** permite la creación de usuarios internos del sistema con configuración completa de plataforma, datos de usuario y asignación de roles por ubicación. Este endpoint está diseñado para ser usado por administradores del sistema.

---

## Objetivo

Proporcionar un endpoint único que permita crear un usuario interno completo en el sistema, ejecutando las siguientes operaciones de manera atómica:

1. Crear configuración de plataforma para el usuario
2. Crear registro de usuario con credenciales
3. Asignar múltiples roles por ubicación al usuario (puede estar en varias ubicaciones con roles diferentes)

### Alcance

**En alcance:**
- Creación de configuración de plataforma
- Creación de usuario con hash de contraseña
- Asignación de múltiples roles por ubicación (un usuario puede tener diferentes roles en diferentes ubicaciones)
- Validaciones de integridad referencial
- Validación de combinaciones únicas (location_id, rol_id)
- Validaciones de negocio
- Transaccionalidad del proceso completo

**Fuera de alcance:**
- Envío de email de bienvenida (puede agregarse después)
- Activación de usuario (se crea activo por defecto)
- Creación de empresas o ubicaciones

---

## Contexto de Negocio

### Problema que Resuelve

Actualmente, crear un usuario interno requiere múltiples llamadas a diferentes endpoints:
1. `POST /platform` - Crear configuración
2. `POST /user` - Crear usuario
3. `POST /user_location_rol` - Asignar rol (una vez por cada ubicación)

Este flujo unifica todo en una sola operación atómica, garantizando consistencia y simplificando el proceso. Además, permite asignar el usuario a múltiples ubicaciones con roles específicos para cada una.

### Beneficios Esperados

- ✅ Simplificación del proceso de alta de usuarios
- ✅ Garantía de atomicidad (todo o nada)
- ✅ Reducción de errores por proceso manual
- ✅ Validaciones centralizadas
- ✅ Soporte para múltiples ubicaciones con roles diferentes
- ✅ Flexibilidad: un usuario puede ser admin en una ubicación y operador en otra
- ✅ Mejor experiencia para administradores

---

## Actores Involucrados

| Actor | Rol | Responsabilidad |
|-------|-----|-----------------|
| **Super Administrador** | Admin del sistema | Crear usuarios internos |
| **Sistema** | Automático | Validar datos, crear registros, generar IDs |

---

## Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────────┐
│                    Request POST /auth/create-user-internal       │
│  {                                                               │
│    language_id, currency_id,                                    │
│    location_rol: [                                              │
│      { location_id: UUID, rol_id: UUID },                       │
│      { location_id: UUID, rol_id: UUID }                        │
│    ],                                                           │
│    email, password, first_name, last_name, ...                  │
│  }                                                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    1. VALIDACIONES PREVIAS                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ ✓ Language existe?                                         │  │
│  │ ✓ Currency existe?                                         │  │
│  │ ✓ location_rol no está vacío?                              │  │
│  │ ✓ Para cada item en location_rol:                          │  │
│  │   ✓ Location existe?                                       │  │
│  │   ✓ Rol existe?                                            │  │
│  │ ✓ No hay combinaciones duplicadas (location, rol)?         │  │
│  │ ✓ Email único (no existe)?                                 │  │
│  │ ✓ Password cumple requisitos?                              │  │
│  └───────────────────────────────────────────────────────────┘  │
│                         │                                         │
│                         ▼ Si todas pasan                          │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              2. CREAR CONFIGURACIÓN DE PLATAFORMA                │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ PlatformSaveUseCase.execute({                              │  │
│  │   language_id: UUID,                                       │  │
│  │   location_id: UUID (primera location de la lista),        │  │
│  │   currency_id: UUID,                                       │  │
│  │   token_expiration_minutes: 60,                            │  │
│  │   refresh_token_expiration_minutes: 1440                   │  │
│  │ })                                                         │  │
│  │                                                            │  │
│  │ → platform_id: UUID (generado)                             │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    3. CREAR USUARIO                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ UserSaveUseCase.execute({                                  │  │
│  │   platform_id: UUID (del paso 2),                          │  │
│  │   email: string,                                           │  │
│  │   password: string (será hasheado),                        │  │
│  │   identification: string,                                  │  │
│  │   first_name: string,                                      │  │
│  │   last_name: string,                                       │  │
│  │   phone: string,                                           │  │
│  │   state: true                                              │  │
│  │ })                                                         │  │
│  │                                                            │  │
│  │ → user_id: UUID (generado)                                 │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│         4. ASIGNAR ROLES POR UBICACIÓN (LOOP)                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Para cada item en location_rol:                            │  │
│  │                                                            │  │
│  │   UserLocationRolSaveUseCase.execute({                     │  │
│  │     user_id: UUID (del paso 3),                            │  │
│  │     location_id: UUID (del item),                          │  │
│  │     rol_id: UUID (del item)                                │  │
│  │   })                                                       │  │
│  │                                                            │  │
│  │   → user_location_rol_id: UUID (generado)                  │  │
│  │                                                            │  │
│  │ Ejemplo:                                                   │  │
│  │   - Sede A + Rol Admin  ✓                                  │  │
│  │   - Sede B + Rol Operador ✓                                │  │
│  │   - Sede A + Rol Auditor ✓ (mismo location, otro rol)      │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              5. RETORNAR MENSAJE DE ÉXITO                        │
│  {                                                               │
│    message_type: "temporary",                                    │
│    notification_type: "success",                                 │
│    message: "Usuario interno creado exitosamente",              │
│    response: null                                                │
│  }                                                               │
│                                                                  │
│  Nota: El mensaje es traducido usando KEYS_MESSAGES              │
│        según el idioma configurado en el header                  │
└─────────────────────────────────────────────────────────────────┘
```

### Estados del Flujo

| Estado | Descripción | Siguiente Estado |
|--------|-------------|-----------------|
| **VALIDATING** | Validando datos de entrada | CREATING_PLATFORM, ERROR |
| **CREATING_PLATFORM** | Creando configuración de plataforma | CREATING_USER, ERROR |
| **CREATING_USER** | Creando registro de usuario | ASSIGNING_ROLE, ERROR |
| **ASSIGNING_ROLE** | Asignando rol y ubicación | COMPLETED, ERROR |
| **COMPLETED** | Usuario creado exitosamente | - |
| **ERROR** | Error en algún paso | - |

---

## Especificación Técnica

### Arquitectura

```
┌──────────────────────────────────────────────────────────────┐
│         Infrastructure/Web Layer                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  POST /auth/create-user-internal                        │  │
│  │  - AuthRouter                                           │  │
│  │  - @check_permissions([PERMISSION_TYPE.SAVE])          │  │
│  │  - @execute_transaction_route                           │  │
│  └──────────────────────┬─────────────────────────────────┘  │
└─────────────────────────┼────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│         Infrastructure/Web/Controller Layer                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  AuthController.create_user_internal()                  │  │
│  │  - Invoca Use Case                                      │  │
│  │  - Construye Response                                   │  │
│  └──────────────────────┬─────────────────────────────────┘  │
└─────────────────────────┼────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│              Domain/Business Use Case Layer                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  CreateUserInternalUseCase.execute()                    │  │
│  │  ├─ 1. Validaciones (Read Use Cases)                    │  │
│  │  │    ├─ LanguageReadUseCase                            │  │
│  │  │    ├─ LocationReadUseCase                            │  │
│  │  │    ├─ CurrencyReadUseCase                            │  │
│  │  │    ├─ RolReadUseCase                                 │  │
│  │  │    └─ UserListUseCase (validar email único)          │  │
│  │  │                                                       │  │
│  │  ├─ 2. PlatformSaveUseCase                              │  │
│  │  ├─ 3. UserSaveUseCase                                  │  │
│  │  └─ 4. UserLocationRolSaveUseCase                       │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### Componentes Principales

#### 1. Models (`src/domain/models/business/auth/create_user_internal/`)

**Archivos a crear:**
- `create_user_internal_request.py`
- `create_user_internal_response.py`
- `index.py`

#### 2. Use Case (`src/domain/services/use_cases/business/auth/create_user_internal/`)

**Archivo a crear:**
- `create_user_internal_use_case.py`

#### 3. Controller (actualizar existente)

**Archivo a actualizar:**
- `src/infrastructure/web/controller/business/auth_controller.py`

#### 4. Router (actualizar existente)

**Archivo a actualizar:**
- `src/infrastructure/web/business_routes/auth_router.py`

---

## Endpoints API

### Endpoint: Create User Internal

```
POST /auth/create-user-internal
```

**Headers:**
```
Authorization: Bearer <token>
Language: es | en
Content-Type: application/json
```

**Restricciones de Acceso:**
- ⚠️ **Rol requerido**: `ADMIN` (solo administradores)
- **Permiso requerido**: `PERMISSION_TYPE.SAVE`
- **Autenticación**: Token JWT válido

**Request Body:**
```json
{
  "language_id": "550e8400-e29b-41d4-a716-446655440000",
  "currency_id": "770e8400-e29b-41d4-a716-446655440000",
  "location_rol": [
    {
      "location_id": "660e8400-e29b-41d4-a716-446655440000",
      "rol_id": "880e8400-e29b-41d4-a716-446655440000"
    },
    {
      "location_id": "660e8400-e29b-41d4-a716-446655440000",
      "rol_id": "990e8400-e29b-41d4-a716-446655440000"
    },
    {
      "location_id": "aa0e8400-e29b-41d4-a716-446655440000",
      "rol_id": "bb0e8400-e29b-41d4-a716-446655440000"
    }
  ],
  "email": "nuevo.usuario@goluti.com",
  "password": "SecurePassword123!",
  "identification": "12345678",
  "first_name": "Juan",
  "last_name": "Pérez",
  "phone": "+573001234567",
  "token_expiration_minutes": 60,
  "refresh_token_expiration_minutes": 1440
}
```

**Nota importante sobre `location_rol`:**
- Es una lista que puede contener múltiples combinaciones de location_id y rol_id
- Permite asignar al usuario a varias ubicaciones con roles específicos
- **Puede repetirse el mismo location_id** pero con **rol_id diferente** (ej: un usuario puede ser ADMIN y AUDITOR en la misma ubicación)
- **No se permiten duplicados exactos** de la combinación (location_id, rol_id)
- La lista **no puede estar vacía** (mínimo 1 asignación)

**Response (Success - 200 OK):**
```json
{
  "message_type": "temporary",
  "notification_type": "success",
  "message": "Usuario interno creado exitosamente",
  "response": null
}
```

**Nota:** El campo `response` es `null` para este endpoint. El mensaje de éxito se obtiene del sistema de traducción usando `KEYS_MESSAGES.AUTH_CREATE_USER_SUCCESS`.

**Response (Error - Validación):**
```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "El rol con ID 880e8400-e29b-41d4-a716-446655440000 no existe en el sistema",
  "response": null
}
```

**Response (Error - Combinación Duplicada):**
```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "La combinación de location_id y rol_id está duplicada en la lista",
  "response": null
}
```

**Response (Error - Lista Vacía):**
```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "Debe proporcionar al menos una asignación de rol y ubicación",
  "response": null
}
```

**Response (Error - Email Duplicado):**
```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "El email ya está registrado en el sistema",
  "response": null
}
```

**Response (Error - Rol No Autorizado - 403):**
```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "Solo usuarios con rol ADMIN pueden crear usuarios internos",
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
- **200 OK**: Usuario creado exitosamente
- **200 OK + error**: Error de validación o negocio (language, currency, location, rol, email duplicado, etc.)
- **401 Unauthorized**: Token inválido o expirado
- **403 Forbidden**: Rol no autorizado (no es ADMIN) o sin permisos (no tiene permiso SAVE)
- **422 Unprocessable Entity**: Error de validación Pydantic (formato de datos incorrecto)

---

## Modelos de Datos

### Request Model

**Archivo**: `src/domain/models/business/auth/create_user_internal/create_user_internal_request.py`

```python
from pydantic import BaseModel, EmailStr, Field, UUID4, field_validator
from typing import Optional, List

class LocationRolItem(BaseModel):
    """
    Modelo para asignación de rol por ubicación.
    
    Permite asignar un usuario a una ubicación con un rol específico.
    Puede haber múltiples items con el mismo location_id pero rol_id diferente.
    """
    location_id: UUID4 = Field(..., description="ID de la ubicación")
    rol_id: UUID4 = Field(..., description="ID del rol")
    
    class Config:
        json_schema_extra = {
            "example": {
                "location_id": "660e8400-e29b-41d4-a716-446655440000",
                "rol_id": "880e8400-e29b-41d4-a716-446655440000"
            }
        }


class CreateUserInternalRequest(BaseModel):
    """
    Modelo de request para creación de usuario interno.
    
    Incluye todos los datos necesarios para:
    - Configuración de plataforma
    - Datos de usuario
    - Asignación de múltiples roles por ubicación
    """
    
    # IDs de configuración (Foreign Keys)
    language_id: UUID4 = Field(..., description="ID del idioma del usuario")
    currency_id: UUID4 = Field(..., description="ID de la moneda")
    
    # Lista de asignaciones de ubicación y rol
    location_rol: List[LocationRolItem] = Field(
        ..., 
        min_length=1,
        description="Lista de asignaciones de rol por ubicación (mínimo 1)"
    )
    
    # Datos del usuario
    email: EmailStr = Field(..., description="Email único del usuario")
    password: str = Field(..., min_length=8, max_length=255, description="Contraseña (será hasheada)")
    identification: str = Field(..., min_length=3, max_length=30, description="Documento de identificación")
    first_name: str = Field(..., min_length=2, max_length=100, description="Primer nombre")
    last_name: str = Field(..., min_length=2, max_length=100, description="Apellido")
    phone: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto")
    
    # Configuración de tokens (opcional)
    token_expiration_minutes: Optional[int] = Field(default=60, ge=5, le=1440, description="Minutos de expiración del token")
    refresh_token_expiration_minutes: Optional[int] = Field(default=1440, ge=60, le=43200, description="Minutos de expiración del refresh token")
    
    @field_validator('location_rol')
    @classmethod
    def validate_no_exact_duplicates(cls, v: List[LocationRolItem]) -> List[LocationRolItem]:
        """
        Valida que no haya combinaciones exactas duplicadas de (location_id, rol_id).
        
        Nota: SÍ se permite el mismo location_id con diferentes rol_id.
        """
        seen = set()
        for item in v:
            combination = (str(item.location_id), str(item.rol_id))
            if combination in seen:
                raise ValueError(
                    f"Combinación duplicada encontrada: location_id={item.location_id}, "
                    f"rol_id={item.rol_id}. No se permiten duplicados exactos."
                )
            seen.add(combination)
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "language_id": "550e8400-e29b-41d4-a716-446655440000",
                "currency_id": "770e8400-e29b-41d4-a716-446655440000",
                "location_rol": [
                    {
                        "location_id": "660e8400-e29b-41d4-a716-446655440000",
                        "rol_id": "880e8400-e29b-41d4-a716-446655440000"
                    },
                    {
                        "location_id": "660e8400-e29b-41d4-a716-446655440000",
                        "rol_id": "990e8400-e29b-41d4-a716-446655440000"
                    },
                    {
                        "location_id": "aa0e8400-e29b-41d4-a716-446655440000",
                        "rol_id": "bb0e8400-e29b-41d4-a716-446655440000"
                    }
                ],
                "email": "nuevo.usuario@goluti.com",
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

### Response Model

**Nota importante**: Este endpoint NO retorna un modelo de respuesta personalizado. Solo retorna el mensaje de éxito con `response: null`.

Por lo tanto, **NO es necesario crear** `CreateUserInternalResponse` ni clases auxiliares (`RolInfo`, `LocationInfo`, etc.).

El use case debe retornar directamente el mensaje de éxito usando el sistema de traducciones:

```python
return await self.message.get_message(
    config=config,
    message=MessageCoreEntity(
        key=KEYS_MESSAGES.AUTH_CREATE_USER_SUCCESS.value,
        params={"count": str(len(assigned_roles_list))}
    ),
)
```

### Index File

**Archivo**: `src/domain/models/business/auth/create_user_internal/index.py`

```python
from .create_user_internal_request import (
    CreateUserInternalRequest,
    LocationRolItem
)

__all__ = [
    "CreateUserInternalRequest",
    "LocationRolItem"
]
```

**Nota**: Solo se exporta el modelo de Request. No hay modelo de Response porque el endpoint retorna `response: null`.

---

## Validaciones y Reglas

### Reglas de Negocio

1. **Email Único**: El email no debe existir en la tabla `user`
2. **Referencias Válidas**: Todos los IDs (language, currency) deben existir
3. **Lista location_rol**: Debe contener al menos 1 asignación
4. **Validación por Item**: Para cada item en `location_rol`:
   - El `location_id` debe existir en la tabla `location`
   - El `rol_id` debe existir en la tabla `rol`
5. **Combinaciones Únicas**: No se permiten duplicados exactos de (location_id, rol_id)
6. **Locations Repetidas Permitidas**: El mismo location_id puede aparecer múltiples veces con diferentes rol_id
7. **Contraseña Segura**: Mínimo 8 caracteres
8. **Estado Inicial**: El usuario se crea activo (`state = true`)
9. **Platform Único**: Cada usuario tiene su propia configuración de plataforma
10. **Atomicidad**: Si falla algún paso (incluyendo cualquier asignación de rol), se debe hacer rollback de toda la operación

### Validaciones Técnicas

**Nota importante**: Todos los mensajes de error usan el sistema de traducciones del proyecto mediante `KEYS_MESSAGES` y `Message().get_message()`.

#### 1. Validación de Language

```python
language = await self.language_read_use_case.execute(
    config=config,
    params=LanguageRead(id=params.language_id)
)

if isinstance(language, str) or not language:
    return await self.message.get_message(
        config=config,
        message=MessageCoreEntity(
            key=KEYS_MESSAGES.AUTH_CREATE_USER_LANGUAGE_NOT_FOUND.value
        ),
    )
```

#### 2. Validación de Currency

```python
currency = await self.currency_read_use_case.execute(
    config=config,
    params=CurrencyRead(id=params.currency_id)
)

if isinstance(currency, str) or not currency:
    return await self.message.get_message(
        config=config,
        message=MessageCoreEntity(
            key=KEYS_MESSAGES.AUTH_CREATE_USER_CURRENCY_NOT_FOUND.value
        ),
    )
```

#### 3. Validación de Lista location_rol No Vacía

```python
if not params.location_rol or len(params.location_rol) == 0:
    return await self.message.get_message(
        config=config,
        message=MessageCoreEntity(
            key=KEYS_MESSAGES.AUTH_CREATE_USER_EMPTY_LOCATION_ROL.value
        ),
    )
```

#### 4. Validación de Locations y Roles en location_rol

```python
validated_items = []

for item in params.location_rol:
    location = await self.location_read_use_case.execute(
        config=config,
        params=LocationRead(id=item.location_id)
    )
    
    if isinstance(location, str) or not location:
        return await self.message.get_message(
            config=config,
            message=MessageCoreEntity(
                key=KEYS_MESSAGES.AUTH_CREATE_USER_LOCATION_NOT_FOUND.value,
                params={"location_id": str(item.location_id)}
            ),
        )
    
    rol = await self.rol_read_use_case.execute(
        config=config,
        params=RolRead(id=item.rol_id)
    )
    
    if isinstance(rol, str) or not rol:
        return await self.message.get_message(
            config=config,
            message=MessageCoreEntity(
                key=KEYS_MESSAGES.AUTH_CREATE_USER_ROL_NOT_FOUND.value,
                params={"rol_id": str(item.rol_id)}
            ),
        )
    
    validated_items.append({
        "location_id": item.location_id,
        "rol_id": item.rol_id,
        "location": location,
        "rol": rol
    })
```

#### 5. Validación de Combinaciones Duplicadas

```python
seen_combinations = set()

for item in params.location_rol:
    combination = (str(item.location_id), str(item.rol_id))
    if combination in seen_combinations:
        return await self.message.get_message(
            config=config,
            message=MessageCoreEntity(
                key=KEYS_MESSAGES.AUTH_CREATE_USER_DUPLICATE_COMBINATION.value
            ),
        )
    seen_combinations.add(combination)
```

#### 6. Validación de Email Único

```python
existing_users = await self.user_list_use_case.execute(
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

if existing_users and not isinstance(existing_users, str):
    return await self.message.get_message(
        config=config,
        message=MessageCoreEntity(
            key=KEYS_MESSAGES.AUTH_CREATE_USER_EMAIL_ALREADY_EXISTS.value
        ),
    )
```

### Nuevas Claves de Traducción Requeridas

**Archivo**: `src/core/enums/keys_message.py`

Agregar las siguientes claves al enum `KEYS_MESSAGES`:

```python
AUTH_CREATE_USER_LANGUAGE_NOT_FOUND = "auth_create_user_language_not_found"
AUTH_CREATE_USER_CURRENCY_NOT_FOUND = "auth_create_user_currency_not_found"
AUTH_CREATE_USER_EMPTY_LOCATION_ROL = "auth_create_user_empty_location_rol"
AUTH_CREATE_USER_LOCATION_NOT_FOUND = "auth_create_user_location_not_found"
AUTH_CREATE_USER_ROL_NOT_FOUND = "auth_create_user_rol_not_found"
AUTH_CREATE_USER_DUPLICATE_COMBINATION = "auth_create_user_duplicate_combination"
AUTH_CREATE_USER_EMAIL_ALREADY_EXISTS = "auth_create_user_email_already_exists"
AUTH_CREATE_USER_SUCCESS = "auth_create_user_success"
```

**Traducciones necesarias en la tabla `translation`:**

| Key | Context | ES (Español) | EN (English) |
|-----|---------|--------------|--------------|
| `auth_create_user_language_not_found` | auth | El idioma especificado no existe en el sistema | The specified language does not exist in the system |
| `auth_create_user_currency_not_found` | auth | La moneda especificada no existe en el sistema | The specified currency does not exist in the system |
| `auth_create_user_empty_location_rol` | auth | Debe proporcionar al menos una asignación de rol y ubicación | You must provide at least one role and location assignment |
| `auth_create_user_location_not_found` | auth | La ubicación con ID {location_id} no existe en el sistema | The location with ID {location_id} does not exist in the system |
| `auth_create_user_rol_not_found` | auth | El rol con ID {rol_id} no existe en el sistema | The role with ID {rol_id} does not exist in the system |
| `auth_create_user_duplicate_combination` | auth | La combinación de location_id y rol_id está duplicada en la lista | The combination of location_id and rol_id is duplicated in the list |
| `auth_create_user_email_already_exists` | auth | El email ya está registrado en el sistema | The email is already registered in the system |
| `auth_create_user_success` | auth | Usuario interno creado exitosamente | Internal user created successfully |

**Nota**: Las traducciones con `{placeholders}` soportan interpolación de parámetros.

---

## Casos de Uso Involucrados

### Use Cases de Validación (Read)

| Use Case | Propósito | Cantidad de Validaciones |
|----------|-----------|--------------------------|
| `LanguageReadUseCase` | Validar que language_id existe | 1 vez |
| `CurrencyReadUseCase` | Validar que currency_id existe | 1 vez |
| `LocationReadUseCase` | Validar que cada location_id existe | N veces (por cada item en location_rol) |
| `RolReadUseCase` | Validar que cada rol_id existe | N veces (por cada item en location_rol) |
| `UserListUseCase` | Validar que email es único | 1 vez |

**Nota**: Si `location_rol` tiene 3 items, se ejecutarán 3 validaciones de Location y 3 de Rol.

### Use Cases de Creación (Save)

| Use Case | Propósito | Cantidad de Ejecuciones |
|----------|-----------|-------------------------|
| `PlatformSaveUseCase` | Crear configuración de plataforma | 1 vez |
| `UserSaveUseCase` | Crear usuario con platform_id | 1 vez |
| `UserLocationRolSaveUseCase` | Asignar rol y ubicación | N veces (por cada item en location_rol) |

**Nota**: Si `location_rol` tiene 3 items, se crearán 3 registros en `user_location_rol`.

---

## Use Case Principal

**Archivo**: `src/domain/services/use_cases/business/auth/create_user_internal/create_user_internal_use_case.py`

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

from src.domain.models.business.auth.create_user_internal.index import (
    CreateUserInternalRequest,
    LocationRolItem
)
from src.domain.models.entities.platform.index import PlatformSave, PlatformRead
from src.domain.models.entities.user.index import UserSave
from src.domain.models.entities.user_location_rol.index import UserLocationRolSave
from src.domain.models.entities.language.index import LanguageRead
from src.domain.models.entities.location.index import LocationRead
from src.domain.models.entities.currency.index import CurrencyRead
from src.domain.models.entities.rol.index import RolRead

from src.domain.services.use_cases.entities.language.language_read_use_case import (
    LanguageReadUseCase
)
from src.domain.services.use_cases.entities.location.location_read_use_case import (
    LocationReadUseCase
)
from src.domain.services.use_cases.entities.currency.currency_read_use_case import (
    CurrencyReadUseCase
)
from src.domain.services.use_cases.entities.rol.rol_read_use_case import (
    RolReadUseCase
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
from src.domain.services.use_cases.entities.user_location_rol.user_location_rol_save_use_case import (
    UserLocationRolSaveUseCase
)

from src.infrastructure.database.repositories.entities.language_repository import (
    LanguageRepository
)
from src.infrastructure.database.repositories.entities.location_repository import (
    LocationRepository
)
from src.infrastructure.database.repositories.entities.currency_repository import (
    CurrencyRepository
)
from src.infrastructure.database.repositories.entities.rol_repository import (
    RolRepository
)
from src.infrastructure.database.repositories.entities.user_repository import (
    UserRepository
)
from src.infrastructure.database.repositories.entities.platform_repository import (
    PlatformRepository
)
from src.infrastructure.database.repositories.entities.user_location_rol_repository import (
    UserLocationRolRepository
)


language_repository = LanguageRepository()
location_repository = LocationRepository()
currency_repository = CurrencyRepository()
rol_repository = RolRepository()
user_repository = UserRepository()
platform_repository = PlatformRepository()
user_location_rol_repository = UserLocationRolRepository()


class CreateUserInternalUseCase:
    """
    Use Case para crear un usuario interno completo en el sistema.
    
    Proceso:
    1. Validar todas las referencias (language, currency, locations, roles, email)
    2. Crear Platform (usando primera ubicación de la lista)
    3. Crear User con password hasheado
    4. Crear múltiples UserLocationRol (iterar sobre location_rol)
    5. Retornar mensaje de éxito traducido
    """
    
    def __init__(self):
        self.language_read_uc = LanguageReadUseCase(language_repository)
        self.location_read_uc = LocationReadUseCase(location_repository)
        self.currency_read_uc = CurrencyReadUseCase(currency_repository)
        self.rol_read_uc = RolReadUseCase(rol_repository)
        self.user_list_uc = UserListUseCase(user_repository)
        
        self.platform_save_uc = PlatformSaveUseCase(platform_repository)
        self.user_save_uc = UserSaveUseCase(user_repository)
        self.user_location_rol_save_uc = UserLocationRolSaveUseCase(
            user_location_rol_repository
        )
        
        self.message = Message()
    
    @execute_transaction(layer=LAYER.D_S_U_B.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: CreateUserInternalRequest,
    ) -> Union[str, None]:
        """
        Ejecuta el flujo completo de creación de usuario interno.
        
        Returns:
            None: Si la creación fue exitosa
            str: Mensaje de error traducido si algo falló
        """
        
        config.response_type = RESPONSE_TYPE.OBJECT
        
        
        language = await self.language_read_uc.execute(
            config=config,
            params=LanguageRead(id=params.language_id)
        )
        if isinstance(language, str) or not language:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_CREATE_USER_LANGUAGE_NOT_FOUND.value
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
                    key=KEYS_MESSAGES.AUTH_CREATE_USER_CURRENCY_NOT_FOUND.value
                ),
            )
        
        
        if not params.location_rol or len(params.location_rol) == 0:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_CREATE_USER_EMPTY_LOCATION_ROL.value
                ),
            )
        
        validated_items = []
        seen_combinations = set()
        
        for item in params.location_rol:
            combination = (str(item.location_id), str(item.rol_id))
            if combination in seen_combinations:
                return await self.message.get_message(
                    config=config,
                    message=MessageCoreEntity(
                        key=KEYS_MESSAGES.AUTH_CREATE_USER_DUPLICATE_COMBINATION.value
                    ),
                )
            seen_combinations.add(combination)
            
            
            location = await self.location_read_uc.execute(
                config=config,
                params=LocationRead(id=item.location_id)
            )
            if isinstance(location, str) or not location:
                return await self.message.get_message(
                    config=config,
                    message=MessageCoreEntity(
                        key=KEYS_MESSAGES.AUTH_CREATE_USER_LOCATION_NOT_FOUND.value,
                        params={"location_id": str(item.location_id)}
                    ),
                )
            
            
            rol = await self.rol_read_uc.execute(
                config=config,
                params=RolRead(id=item.rol_id)
            )
            if isinstance(rol, str) or not rol:
                return await self.message.get_message(
                    config=config,
                    message=MessageCoreEntity(
                        key=KEYS_MESSAGES.AUTH_CREATE_USER_ROL_NOT_FOUND.value,
                        params={"rol_id": str(item.rol_id)}
                    ),
                )
            
            validated_items.append({
                "location_id": item.location_id,
                "rol_id": item.rol_id,
                "location": location,
                "rol": rol
            })
        
        
        existing_users = await self.user_list_uc.execute(
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
        if existing_users and not isinstance(existing_users, str):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_CREATE_USER_EMAIL_ALREADY_EXISTS.value
                ),
            )
        
        
        first_location_id = params.location_rol[0].location_id
        
        platform_created = await self.platform_save_uc.execute(
            config=config,
            params=PlatformSave(
                language_id=params.language_id,
                location_id=first_location_id,
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
                password=params.password,  # Será hasheado en UserSaveUseCase
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
        
        
        for validated_item in validated_items:
            user_location_rol_created = await self.user_location_rol_save_uc.execute(
                config=config,
                params=UserLocationRolSave(
                    user_id=user_created.id,
                    location_id=validated_item["location_id"],
                    rol_id=validated_item["rol_id"]
                )
            )
            
            if isinstance(user_location_rol_created, str) or not user_location_rol_created:
                return await self.message.get_message(
                    config=config,
                    message=MessageCoreEntity(
                        key=KEYS_MESSAGES.CORE_ERROR_SAVING_RECORD.value
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
async def create_user_internal(
    self, 
    config: Config, 
    params: CreateUserInternalRequest
) -> Response[None]:
    result = await self.create_user_internal_use_case.execute(
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
                key=KEYS_MESSAGES.AUTH_CREATE_USER_SUCCESS.value
            ),
        ),
    )
```

**Lógica del Controller:**
- Si el Use Case retorna `str` → Error → `Response.error(None, result)`
- Si el Use Case retorna `None` → Éxito → `Response.success_temporary_message(response=None, message=...)`

---

## Manejo de Errores

| Error | Código HTTP | Mensaje | Solución |
|-------|-------------|---------|----------|
| Language no existe | 200 | "El idioma especificado no existe" | Verificar language_id |
| Currency no existe | 200 | "La moneda especificada no existe" | Verificar currency_id |
| Lista vacía | 200 | "Debe proporcionar al menos una asignación de rol y ubicación" | Enviar al menos 1 item en location_rol |
| Combinación duplicada | 200 | "La combinación de location_id y rol_id está duplicada en la lista" | Eliminar duplicados en location_rol |
| Location no existe | 200 | "La ubicación con ID {id} no existe" | Verificar cada location_id en la lista |
| Rol no existe | 200 | "El rol con ID {id} no existe" | Verificar cada rol_id en la lista |
| Email duplicado | 200 | "El email ya está registrado" | Usar otro email |
| Error en Platform | 200 | "Error al crear configuración" | Revisar logs |
| Error en User | 200 | "Error al crear usuario" | Revisar logs |
| Error en UserLocationRol | 200 | "Error al asignar rol en {location}" | Revisar logs |
| Rol no autorizado | 403 | "Solo usuarios con rol ADMIN pueden crear usuarios internos" | Debe tener rol ADMIN |
| Sin permisos | 403 | "No tiene permisos para realizar esta acción" | Debe tener permiso SAVE |
| Token inválido | 401 | "Token inválido o expirado" | Renovar token |

**Nota importante sobre errores**:
- Todos los errores de validación retornan código 200 con mensaje descriptivo dentro del response estándar de la API.
- Si ocurre un error en cualquiera de las asignaciones de `user_location_rol`, se hace rollback de toda la transacción (Platform, User, y todas las asignaciones creadas hasta ese momento).

---

## Seguridad

### Permisos Requeridos

```python
@check_permissions([PERMISSION_TYPE.SAVE.value])
@check_roles(["ADMIN"])  # Solo rol ADMIN
```

**Restricción de Rol:**
- ⚠️ **Solo usuarios con rol `ADMIN`** pueden consumir este endpoint
- El rol debe estar activo y vigente
- El usuario debe tener el permiso `SAVE` asociado a su rol

**Validación en el Router:**
```python
@auth_router.post(
    "/create-user-internal",
    status_code=status.HTTP_200_OK,
    response_model=Response[None]
)
@check_permissions([PERMISSION_TYPE.SAVE.value])
@check_roles(["ADMIN"])
@execute_transaction_route(enabled=settings.has_track)
async def create_user_internal(
    params: CreateUserInternalRequest,
    config: Config = Depends(get_config)
) -> Response[None]:
    return await auth_controller.create_user_internal(config=config, params=params)
```

**Nota**: El `response_model` es `Response[None]` porque el campo `response` será `null`.

### Validaciones de Seguridad

1. **Validación de Rol**: Solo rol `ADMIN` puede crear usuarios internos
2. **Validación de Permiso**: Requiere permiso `SAVE`
3. **Hash de Contraseña**: La contraseña se hashea con bcrypt en `UserSaveUseCase`
4. **Token JWT**: Validación en cada request
5. **Rate Limiting**: Aplicar límite (ej: 10 creaciones/hora por admin)
6. **Auditoría**: El decorador `@execute_transaction` registra la operación con información del usuario admin que ejecuta la acción

### Consideraciones Adicionales

- **No exponer contraseñas**: La respuesta no incluye la contraseña
- **HTTPS**: Siempre usar en producción
- **Validación de entrada**: Pydantic valida tipos y formatos
- **Segregación de responsabilidades**: Solo administradores pueden crear usuarios internos

---

## Ejemplos de Uso

### Caso de Uso 1: Crear Administrador con Múltiples Ubicaciones

**Escenario**: María será administradora en la Sede Principal y auditora en la Sede Norte.

**Request:**
```bash
curl -X POST https://api.goluti.com/auth/create-user-internal \
  -H "Authorization: Bearer TOKEN" \
  -H "Language: es" \
  -H "Content-Type: application/json" \
  -d '{
    "language_id": "550e8400-e29b-41d4-a716-446655440000",
    "currency_id": "770e8400-e29b-41d4-a716-446655440000",
    "location_rol": [
      {
        "location_id": "660e8400-e29b-41d4-a716-446655440000",
        "rol_id": "880e8400-e29b-41d4-a716-446655440000"
      },
      {
        "location_id": "aa0e8400-e29b-41d4-a716-446655440000",
        "rol_id": "990e8400-e29b-41d4-a716-446655440000"
      }
    ],
    "email": "admin@goluti.com",
    "password": "AdminPassword123!",
    "identification": "87654321",
    "first_name": "María",
    "last_name": "González",
    "phone": "+573009876543"
  }'
```

**Response:**
```json
{
  "message_type": "temporary",
  "notification_type": "success",
  "message": "Usuario interno creado exitosamente",
  "response": null
}
```

### Caso de Uso 2: Usuario con Misma Ubicación pero Diferentes Roles

**Escenario**: Juan será administrador Y auditor en la misma Sede Principal.

**Request:**
```bash
curl -X POST https://api.goluti.com/auth/create-user-internal \
  -H "Authorization: Bearer TOKEN" \
  -H "Language: es" \
  -H "Content-Type: application/json" \
  -d '{
    "language_id": "550e8400-e29b-41d4-a716-446655440000",
    "currency_id": "770e8400-e29b-41d4-a716-446655440000",
    "location_rol": [
      {
        "location_id": "660e8400-e29b-41d4-a716-446655440000",
        "rol_id": "880e8400-e29b-41d4-a716-446655440000"
      },
      {
        "location_id": "660e8400-e29b-41d4-a716-446655440000",
        "rol_id": "990e8400-e29b-41d4-a716-446655440000"
      }
    ],
    "email": "juan.perez@goluti.com",
    "password": "SecurePass123!",
    "identification": "12345678",
    "first_name": "Juan",
    "last_name": "Pérez",
    "phone": "+573001234567"
  }'
```

**Response:**
```json
{
  "message_type": "temporary",
  "notification_type": "success",
  "message": "Usuario interno creado exitosamente",
  "response": null
}
```

**Nota**: Juan puede tener ambos roles en la misma ubicación.

### Caso de Uso 3: Error - Combinación Duplicada

**Request:**
```bash
curl -X POST https://api.goluti.com/auth/create-user-internal \
  -H "Authorization: Bearer TOKEN" \
  -H "Language: es" \
  -d '{
    "location_rol": [
      {
        "location_id": "660e8400-e29b-41d4-a716-446655440000",
        "rol_id": "880e8400-e29b-41d4-a716-446655440000"
      },
      {
        "location_id": "660e8400-e29b-41d4-a716-446655440000",
        "rol_id": "880e8400-e29b-41d4-a716-446655440000"
      }
    ],
    ...
  }'
```

**Response:**
```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "La combinación de location_id y rol_id está duplicada en la lista",
  "response": null
}
```

### Caso de Uso 4: Error - Email Duplicado

**Request:**
```bash
curl -X POST https://api.goluti.com/auth/create-user-internal \
  -H "Authorization: Bearer TOKEN" \
  -H "Language: es" \
  -d '{
    "email": "admin@goluti.com",
    ...
  }'
```

**Response:**
```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "El email ya está registrado en el sistema",
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
│                   └── create_user_internal/
│                       └── test_create_user_internal_use_case.py
└── infrastructure/
    └── web/
        ├── controller/
        │   └── business/
        │       └── test_auth_controller.py
        └── business_routes/
            └── test_auth_router.py
```

### Unit Tests

**Archivo**: `src/tests/domain/services/use_cases/business/auth/create_user_internal/test_create_user_internal_use_case.py`

```python
import pytest
from src.domain.services.use_cases.business.auth.create_user_internal.create_user_internal_use_case import (
    CreateUserInternalUseCase
)
from src.domain.models.business.auth.create_user_internal.index import (
    CreateUserInternalRequest,
    LocationRolItem
)

@pytest.mark.asyncio
async def test_create_user_internal_success_multiple_locations(mock_config):
    """Test creación exitosa de usuario interno con múltiples ubicaciones"""
    request = CreateUserInternalRequest(
        language_id="lang-uuid",
        currency_id="curr-uuid",
        location_rol=[
            LocationRolItem(location_id="loc-1-uuid", rol_id="rol-admin-uuid"),
            LocationRolItem(location_id="loc-2-uuid", rol_id="rol-operator-uuid")
        ],
        email="test@goluti.com",
        password="SecurePass123!",
        identification="12345678",
        first_name="Test",
        last_name="User",
        phone="+573001234567"
    )
    
    use_case = CreateUserInternalUseCase()
    result = await use_case.execute(config=mock_config, params=request)
    
    assert result is not None
    assert not isinstance(result, str)
    assert result.email == request.email
    assert len(result.assigned_roles) == 2

@pytest.mark.asyncio
async def test_create_user_internal_same_location_different_roles(mock_config):
    """Test usuario con múltiples roles en la misma ubicación"""
    request = CreateUserInternalRequest(
        language_id="lang-uuid",
        currency_id="curr-uuid",
        location_rol=[
            LocationRolItem(location_id="loc-1-uuid", rol_id="rol-admin-uuid"),
            LocationRolItem(location_id="loc-1-uuid", rol_id="rol-auditor-uuid")
        ],
        email="test@goluti.com",
        password="SecurePass123!",
        identification="12345678",
        first_name="Test",
        last_name="User"
    )
    
    use_case = CreateUserInternalUseCase()
    result = await use_case.execute(config=mock_config, params=request)
    
    assert result is not None
    assert not isinstance(result, str)
    assert len(result.assigned_roles) == 2
    assert result.assigned_roles[0].location.id == result.assigned_roles[1].location.id

@pytest.mark.asyncio
async def test_create_user_internal_duplicate_combination(mock_config):
    """Test error por combinación duplicada"""
    with pytest.raises(ValueError, match="Combinación duplicada"):
        request = CreateUserInternalRequest(
            language_id="lang-uuid",
            currency_id="curr-uuid",
            location_rol=[
                LocationRolItem(location_id="loc-1-uuid", rol_id="rol-admin-uuid"),
                LocationRolItem(location_id="loc-1-uuid", rol_id="rol-admin-uuid")  # Duplicado
            ],
            email="test@goluti.com",
            password="SecurePass123!",
            identification="12345678",
            first_name="Test",
            last_name="User"
        )

@pytest.mark.asyncio
async def test_create_user_internal_empty_list(mock_config):
    """Test error por lista vacía"""
    with pytest.raises(ValueError, match="al menos"):
        request = CreateUserInternalRequest(
            language_id="lang-uuid",
            currency_id="curr-uuid",
            location_rol=[],  # Lista vacía
            email="test@goluti.com",
            password="SecurePass123!",
            identification="12345678",
            first_name="Test",
            last_name="User"
        )

@pytest.mark.asyncio
async def test_create_user_internal_email_duplicate(mock_config, duplicate_email_request):
    """Test error por email duplicado"""
    use_case = CreateUserInternalUseCase()
    result = await use_case.execute(config=mock_config, params=duplicate_email_request)
    
    assert isinstance(result, str)
    assert "email" in result.lower()

@pytest.mark.asyncio
async def test_create_user_internal_invalid_rol(mock_config):
    """Test error por rol inválido"""
    request = CreateUserInternalRequest(
        language_id="lang-uuid",
        currency_id="curr-uuid",
        location_rol=[
            LocationRolItem(location_id="loc-1-uuid", rol_id="invalid-rol-uuid")
        ],
        email="test@goluti.com",
        password="SecurePass123!",
        identification="12345678",
        first_name="Test",
        last_name="User"
    )
    
    use_case = CreateUserInternalUseCase()
    result = await use_case.execute(config=mock_config, params=request)
    
    assert isinstance(result, str)
    assert "rol" in result.lower()
```

### Integration Tests

**Archivo**: `src/tests/infrastructure/web/business_routes/test_auth_router.py`

```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_create_user_internal_endpoint_success(client: TestClient, admin_token):
    """Test endpoint completo con token de admin"""
    response = client.post(
        "/auth/create-user-internal",
        headers={
            "Authorization": f"Bearer {admin_token}",
            "Language": "es"
        },
        json={
            "language_id": "lang-uuid",
            "currency_id": "curr-uuid",
            "location_rol": [
                {"location_id": "loc-1", "rol_id": "rol-1"},
                {"location_id": "loc-2", "rol_id": "rol-2"}
            ],
            "email": "test@goluti.com",
            "password": "SecurePass123!",
            "identification": "12345678",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["notification_type"] == "success"
    assert data["response"] is None
    assert "2" in data["message"]

@pytest.mark.asyncio
async def test_create_user_internal_forbidden_non_admin(client: TestClient, user_token):
    """Test que usuario sin rol ADMIN no puede acceder"""
    response = client.post(
        "/auth/create-user-internal",
        headers={
            "Authorization": f"Bearer {user_token}",
            "Language": "es"
        },
        json={}
    )
    
    assert response.status_code == 403
```

**Escenarios de Integration Tests:**

- ✅ Probar flujo completo con base de datos real
- ✅ Validar rollback en caso de error (transacción atómica)
- ✅ Verificar que se crean los registros correctos:
  - 1 registro en `platform`
  - 1 registro en `user`
  - N registros en `user_location_rol` (según la cantidad en `location_rol`)
- ✅ Probar escenario de múltiples ubicaciones con diferentes roles
- ✅ Probar escenario de misma ubicación con diferentes roles
- ✅ Validar que el rollback funciona si falla cualquier asignación
- ✅ Validar restricción de rol ADMIN
- ✅ Validar permisos SAVE
- ✅ Validar response con `response: null`

---

## Referencias

- **[03-00] Business Flow Overview**: Patrón de Business Flow
- **[02-00] Entity Flow Overview**: Use Cases de entidades utilizados
- **[03-05] Auth Flow Specification**: Otros flujos de autenticación
- **[05-02] Database Entities**: Entidades de base de datos involucradas

---

## Historial de Cambios

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0 | Nov 2024 | Creación inicial de especificación | Equipo de Desarrollo Goluti |
| 1.1 | Nov 2024 | Actualización para soportar múltiples asignaciones de ubicación-rol mediante lista `location_rol`. Permite asignar usuario a múltiples ubicaciones con roles diferentes, o misma ubicación con múltiples roles. | Equipo de Desarrollo Goluti |
| 1.2 | Nov 2024 | Especificación de restricción de acceso: solo usuarios con rol ADMIN pueden consumir este endpoint. Actualización de validaciones de seguridad y manejo de errores 403. | Equipo de Desarrollo Goluti |
| 1.3 | Nov 2024 | Integración del sistema de traducciones del proyecto. Todos los mensajes de error ahora usan `KEYS_MESSAGES` y `Message().get_message()`. Definición de 8 nuevas claves de traducción con soporte para ES/EN. | Equipo de Desarrollo Goluti |
| 1.4 | Nov 2024 | Simplificación de respuesta: el endpoint retorna solo mensaje de éxito con `response: null`. Eliminación del modelo `CreateUserInternalResponse` y clases auxiliares. El use case retorna directamente el mensaje traducido. | Equipo de Desarrollo Goluti |
| 1.5 | Nov 2024 | Eliminación de todos los comentarios del código. Código limpio sin comentarios para producción. Corrección de mensajes hardcodeados para usar sistema de traducciones consistentemente. Response tipado como `Response[None]`. Documentación de estructura espejo de tests. | Equipo de Desarrollo Goluti |
| 1.6 | Nov 2024 | Actualización del patrón Controller/Use Case: el use case ahora retorna `Union[str, None]` (None en éxito, str en error). El Controller maneja el mensaje de éxito usando `KEYS_MESSAGES.AUTH_CREATE_USER_SUCCESS`. Eliminación del parámetro `{count}` del mensaje de éxito. Documentación completa del Controller. | Equipo de Desarrollo Goluti |

---

**Fin del Documento**


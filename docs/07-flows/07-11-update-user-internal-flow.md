# 07-11: Flujo de Actualización de Usuario Interno

## Información del Documento

| Campo | Detalle |
|-------|---------|
| **Versión** | 1.0 |
| **Última Actualización** | Diciembre 2024 |
| **Autor** | Equipo de Desarrollo Goluti |
| **Estado** | Activo |

---

## Resumen Ejecutivo

Este documento especifica el flujo para actualizar usuarios internos del sistema. El endpoint permite a un administrador modificar los datos personales y el rol de un usuario que pertenezca a su misma ubicación.

---

## Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Endpoint](#endpoint)
3. [Diagrama de Flujo](#diagrama-de-flujo)
4. [Modelos de Datos](#modelos-de-datos)
5. [Casos de Uso](#casos-de-uso)
6. [Validaciones](#validaciones)
7. [Códigos de Error](#códigos-de-error)
8. [Seguridad](#seguridad)
9. [Ejemplos](#ejemplos)

---

## Descripción General

### Propósito

Permitir que un administrador actualice la información de usuarios internos que pertenezcan a su misma ubicación.

### Alcance

- Actualización de datos personales (nombre, apellido, teléfono)
- Actualización de rol del usuario en la ubicación
- Validación de pertenencia a la misma ubicación
- Validación para evitar dejar la ubicación sin administradores

### Restricciones

| Restricción | Valor |
|-------------|-------|
| Rol requerido | `ADMIN` |
| Permiso requerido | `UPDATE` |
| Ubicación | Mismo `location_id` del admin |

---

## Endpoint

### Especificación

```
PUT /api/v1/auth/update-user-internal/{user_id}
```

### Headers Requeridos

| Header | Valor | Descripción |
|--------|-------|-------------|
| `Authorization` | `Bearer {token}` | Token JWT válido |
| `Content-Type` | `application/json` | Tipo de contenido |

### Path Parameters

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `user_id` | UUID | Sí | ID del usuario a actualizar |

### Request Body

```json
{
  "password": "NewSecurePassword123!",
  "email": "usuario@goluti.com",
  "identification": "12345678",
  "first_name": "Juan",
  "last_name": "Pérez García",
  "phone": "+573001234567",
  "state": true,
  "rol_id": "880e8400-e29b-41d4-a716-446655440000"
}
```

### Response

**Éxito (200 OK):**
```json
{
  "data": {
    "message": "Usuario interno actualizado exitosamente"
  },
  "message": "Usuario interno actualizado exitosamente",
  "notification_type": "success",
  "message_type": "temporary"
}
```

**Error (400 Bad Request):**
```json
{
  "data": null,
  "message": "El usuario no pertenece a su ubicación",
  "notification_type": "error",
  "message_type": "temporary"
}
```

---

## Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────────┐
│                    UPDATE USER INTERNAL                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. VALIDAR USUARIO EXISTE                                        │
│    - UserReadUseCase(user_id)                                    │
│    - Si no existe → Error AUTH_UPDATE_USER_NOT_FOUND             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. VALIDAR NO ES AUTO-EDICIÓN DE ROL CRÍTICO                    │
│    - Si user_id == config.token.user_id                          │
│    - Y se intenta cambiar de ADMIN a otro rol                    │
│    - → Error AUTH_UPDATE_USER_CANNOT_DEMOTE_SELF                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. OBTENER USER_LOCATION_ROLS DEL USUARIO                        │
│    - UserLocationRolListUseCase(user_id)                         │
│    - Si error → Error AUTH_UPDATE_USER_ERROR_FETCHING_ROLES      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. VALIDAR PERTENENCIA A MISMA UBICACIÓN                         │
│    - Verificar que algún user_location_rol                       │
│      tenga location_id == config.token.location_id               │
│    - Si no pertenece → Error AUTH_UPDATE_USER_NOT_IN_LOCATION    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. SI SE CAMBIA ROL: VALIDAR NO DEJAR SIN ADMIN                  │
│    - Si el usuario actual tiene rol ADMIN                        │
│    - Y se cambia a otro rol                                      │
│    - Verificar que haya otros ADMIN en la ubicación              │
│    - Si es último ADMIN → Error AUTH_UPDATE_USER_LAST_ADMIN      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. VALIDAR ROL DESTINO EXISTE (si se envía)                      │
│    - RolReadUseCase(rol_id)                                      │
│    - Si no existe → Error AUTH_UPDATE_USER_ROL_NOT_FOUND         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. ACTUALIZAR DATOS DEL USUARIO                                  │
│    - UserUpdateUseCase(user data)                                │
│    - Si error → Error AUTH_UPDATE_USER_ERROR                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. ACTUALIZAR ROL (si se envió)                                  │
│    - UserLocationRolUpdateUseCase(user_location_rol)             │
│    - Si error → Error AUTH_UPDATE_USER_ERROR_UPDATING_ROL        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 9. RETORNAR ÉXITO                                                │
│    - Mensaje: AUTH_UPDATE_USER_SUCCESS                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Modelos de Datos

### Request Model

```python
class UpdateUserInternalRequest(BaseModel):
    password: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    identification: Optional[str] = Field(None, max_length=30)
    first_name: Optional[str] = Field(None, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    state: Optional[bool] = Field(None)
    rol_id: Optional[UUID4] = Field(None, description="Nuevo rol para el usuario")

    class Config:
        json_schema_extra = {
            "example": {
                "password": "NewSecurePassword123!",
                "email": "usuario@goluti.com",
                "identification": "12345678",
                "first_name": "Juan",
                "last_name": "Pérez García",
                "phone": "+573001234567",
                "state": True,
                "rol_id": "880e8400-e29b-41d4-a716-446655440000"
            }
        }
```

### Response Model

```python
class UpdateUserInternalResponse(BaseModel):
    message: str = Field(...)
```

---

## Casos de Uso

### Caso de Uso Principal: UpdateUserInternalUseCase

```python
class UpdateUserInternalUseCase:
    """
    Actualiza un usuario interno existente.
    
    Validaciones:
    1. Usuario existe
    2. No auto-degradación de rol
    3. Usuario pertenece a la misma ubicación del admin
    4. Si cambia rol ADMIN, verificar que no sea el último
    5. Rol destino existe (si se envía)
    
    Acciones:
    1. Actualizar datos del usuario (nombre, apellido, teléfono)
    2. Actualizar rol si se envía
    """
```

---

## Validaciones

### Reglas de Negocio

1. **Usuario Existe**: El `user_id` debe existir en la tabla `user`
2. **Mismo Location**: El usuario a editar debe pertenecer a la misma ubicación del admin (`config.token.location_id`)
3. **No Auto-Degradación**: Un admin no puede quitarse el rol de ADMIN a sí mismo
4. **Protección Último Admin**: Si el usuario tiene rol ADMIN y se cambia a otro rol, debe haber al menos otro ADMIN en la ubicación
5. **Rol Válido**: Si se envía `rol_id`, debe existir en la tabla `rol`

### Campos Editables

| Campo | Editable | Restricciones |
|-------|----------|---------------|
| `password` | ✅ | Máximo 255 caracteres |
| `email` | ✅ | Máximo 255 caracteres |
| `identification` | ✅ | Máximo 30 caracteres |
| `first_name` | ✅ | Máximo 255 caracteres |
| `last_name` | ✅ | Máximo 255 caracteres |
| `phone` | ✅ | Máximo 20 caracteres |
| `state` | ✅ | Booleano (activo/inactivo) |
| `rol_id` | ✅ | Debe existir, validación de último admin |

---

## Códigos de Error

### Keys de Mensajes

```python
AUTH_UPDATE_USER_NOT_FOUND = "auth_update_user_not_found"
AUTH_UPDATE_USER_NOT_IN_LOCATION = "auth_update_user_not_in_location"
AUTH_UPDATE_USER_CANNOT_DEMOTE_SELF = "auth_update_user_cannot_demote_self"
AUTH_UPDATE_USER_LAST_ADMIN = "auth_update_user_last_admin"
AUTH_UPDATE_USER_ROL_NOT_FOUND = "auth_update_user_rol_not_found"
AUTH_UPDATE_USER_ERROR_FETCHING_ROLES = "auth_update_user_error_fetching_roles"
AUTH_UPDATE_USER_ERROR = "auth_update_user_error"
AUTH_UPDATE_USER_ERROR_UPDATING_ROL = "auth_update_user_error_updating_rol"
AUTH_UPDATE_USER_SUCCESS = "auth_update_user_success"
```

### Traducciones

| Key | ES | EN |
|-----|----|----|
| `auth_update_user_not_found` | El usuario con ID {user_id} no existe en el sistema | The user with ID {user_id} does not exist in the system |
| `auth_update_user_not_in_location` | El usuario no pertenece a su ubicación | The user does not belong to your location |
| `auth_update_user_cannot_demote_self` | No puede quitarse el rol de administrador a sí mismo | You cannot remove the administrator role from yourself |
| `auth_update_user_last_admin` | Este usuario es el único administrador de la ubicación. Debe asignar rol de administrador a otro usuario primero | This user is the only administrator for this location. You must assign the administrator role to another user first |
| `auth_update_user_rol_not_found` | El rol especificado no existe | The specified role does not exist |
| `auth_update_user_error_fetching_roles` | Error al obtener los roles del usuario | Error fetching user roles |
| `auth_update_user_error` | Error al actualizar el usuario | Error updating user |
| `auth_update_user_error_updating_rol` | Error al actualizar el rol del usuario | Error updating user role |
| `auth_update_user_success` | Usuario interno actualizado exitosamente | Internal user updated successfully |

---

## Seguridad

### Control de Acceso

1. **Validación de Rol**: Solo rol `ADMIN` puede editar usuarios internos
2. **Validación de Permiso**: Requiere permiso `UPDATE`
3. **Token JWT**: Validación en cada request
4. **Validación de Location**: El usuario a editar debe pertenecer a la misma ubicación del admin (`config.token.location_id`)
5. **Protección Anti-Degradación**: Un admin no puede degradarse a sí mismo
6. **Protección Último Admin**: Evita dejar una ubicación sin administradores

### Decoradores

```python
@auth_router.put(
    "/update-user-internal/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=Response[UpdateUserInternalResponse]
)
@check_permissions([PERMISSION_TYPE.UPDATE.value])
@check_roles([ROL_TYPE.ADMIN.value])
@execute_transaction_route(enabled=settings.has_track)
async def update_user_internal(
    user_id: UUID = Path(..., description="ID del usuario interno a actualizar"),
    params: UpdateUserInternalRequest,
    config: Config = Depends(get_config)
) -> Response[UpdateUserInternalResponse]:
    return await auth_controller.update_user_internal(
        config=config, 
        user_id=user_id, 
        params=params
    )
```

---

## Ejemplos

### Ejemplo 1: Actualizar Nombre y Teléfono

**Request:**
```bash
PUT /api/v1/auth/update-user-internal/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
  "first_name": "Juan Carlos",
  "last_name": "Pérez García",
  "phone": "+573009876543"
}
```

**Response:**
```json
{
  "data": {
    "message": "Usuario interno actualizado exitosamente"
  },
  "message": "Usuario interno actualizado exitosamente",
  "notification_type": "success",
  "message_type": "temporary"
}
```

### Ejemplo 2: Cambiar Rol del Usuario

**Request:**
```bash
PUT /api/v1/auth/update-user-internal/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
  "rol_id": "990e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**
```json
{
  "data": {
    "message": "Usuario interno actualizado exitosamente"
  },
  "message": "Usuario interno actualizado exitosamente",
  "notification_type": "success",
  "message_type": "temporary"
}
```

### Ejemplo 3: Error - Usuario No Encontrado

**Response:**
```json
{
  "data": null,
  "message": "El usuario con ID 550e8400-e29b-41d4-a716-446655440000 no existe en el sistema",
  "notification_type": "error",
  "message_type": "temporary"
}
```

### Ejemplo 4: Error - Usuario de Otra Ubicación

**Response:**
```json
{
  "data": null,
  "message": "El usuario no pertenece a su ubicación",
  "notification_type": "error",
  "message_type": "temporary"
}
```

### Ejemplo 5: Error - Último Administrador

**Response:**
```json
{
  "data": null,
  "message": "Este usuario es el único administrador de la ubicación. Debe asignar rol de administrador a otro usuario primero",
  "notification_type": "error",
  "message_type": "temporary"
}
```

---

## Historial de Cambios

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0 | Dic 2024 | Creación inicial del flujo Update User Internal | Equipo de Desarrollo Goluti |

---

*Documento generado para el proyecto Goluti Platform*


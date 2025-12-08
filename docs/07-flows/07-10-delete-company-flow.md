# Flujo de Eliminación de Compañía (Delete Company)

**Versión**: 1.0  
**Fecha**: Diciembre 5, 2024  
**Estado**: Especificado  
**Autor(es)**: Equipo de Desarrollo Goluti  

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

El flujo de **Delete Company** permite la eliminación de una compañía del sistema. Este proceso implementa dos estrategias de eliminación:

1. **Hard Delete**: Eliminación física de todos los registros relacionados cuando la compañía no tiene relaciones activas
2. **Soft Delete**: Inactivación de la compañía (`state = false`) cuando tiene relaciones activas o falla el hard delete

Este endpoint está **restringido a administradores** que pertenezcan a la compañía que desean eliminar.

---

## Objetivo

Proporcionar un endpoint que permita eliminar una compañía del sistema, ejecutando las siguientes operaciones de manera atómica:

1. Validar que el admin pertenece a la compañía
2. Verificar relaciones activas (usuarios, transacciones, etc.)
3. Si es posible hacer hard delete:
   - Eliminar UserLocationRol de todos los usuarios
   - Eliminar Users de la compañía
   - Eliminar Platform de cada usuario
   - Eliminar MenuPermissions de los menús de la compañía
   - Eliminar Menus de la compañía
   - Eliminar Locations de la compañía
   - Eliminar Company
4. Si no es posible hacer hard delete:
   - Soft delete (inactivar compañía con `state = false`)
   - Retornar mensaje indicando que será eliminada después de 1 mes

### Alcance

**En alcance:**
- Eliminación de compañía por administrador de la misma
- Verificación de relaciones activas antes de eliminar
- Soft delete como fallback cuando no se puede hacer hard delete
- Eliminación en cascada de todas las entidades relacionadas
- Validaciones de seguridad y permisos

**Fuera de alcance:**
- Eliminación por super admin de cualquier compañía
- Proceso automatizado de eliminación después de 1 mes (soft delete)
- Backup de datos antes de eliminar

---

## Contexto de Negocio

### Problema que Resuelve

Actualmente no existe un mecanismo para eliminar compañías del sistema. Este flujo permite:
1. Cerrar compañías que ya no operan
2. Limpiar datos de prueba
3. Cumplir con solicitudes de eliminación de datos (GDPR, etc.)

### Reglas de Negocio Importantes

1. **Solo Admin de la Compañía**: Solo un usuario con rol ADMIN que pertenezca a una ubicación de esa compañía puede eliminarla

2. **Relaciones Activas**: Si la compañía tiene transacciones, órdenes u otras relaciones de negocio activas, no se puede hacer hard delete

3. **Soft Delete como Fallback**: Si no se puede eliminar físicamente:
   - La compañía se inactiva (`state = false`)
   - Se programa para eliminación permanente después de 1 mes
   - Los usuarios no podrán acceder pero los datos se preservan temporalmente

4. **Eliminación en Cascada**: El hard delete elimina TODAS las entidades relacionadas:
   - Company
   - Locations (todas)
   - Menus (todos los clonados)
   - MenuPermissions
   - Users (todos)
   - UserLocationRol
   - Platform (de cada usuario)

### Beneficios Esperados

- ✅ Gestión del ciclo de vida completo de compañías
- ✅ Cumplimiento con regulaciones de protección de datos
- ✅ Limpieza de datos obsoletos
- ✅ Seguridad: solo admins pueden eliminar su propia compañía

---

## Actores Involucrados

| Actor | Rol | Responsabilidad |
|-------|-----|-----------------|
| **Administrador** | Admin de la compañía | Solicitar eliminación de la compañía |
| **Sistema** | Automático | Validar permisos, verificar relaciones, ejecutar eliminación |

---

## Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────────┐
│           Request DELETE /auth/delete-company/{company_id}       │
│                                                                   │
│  Headers:                                                         │
│    Authorization: Bearer {token}                                  │
│                                                                   │
│  Path Params:                                                     │
│    company_id: UUID                                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DECORADORES DE SEGURIDAD                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ @check_permissions([PERMISSION_TYPE.DELETE.value])        │  │
│  │ @check_roles([ROL_TYPE.ADMIN.value])                      │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    1. VALIDAR COMPAÑÍA EXISTE                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ CompanyReadUseCase.execute({id: company_id})              │  │
│  │                                                            │  │
│  │ Si no existe → Error: "Compañía no encontrada"            │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│            2. VALIDAR ADMIN PERTENECE A LA COMPAÑÍA              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Obtener location_id del token del admin                    │  │
│  │ Verificar que location.company_id == company_id            │  │
│  │                                                            │  │
│  │ Si no pertenece → Error: "No autorizado"                   │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              3. VERIFICAR RELACIONES ACTIVAS                     │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ CheckCompanyActiveRelationsUseCase.execute(company_id)    │  │
│  │                                                            │  │
│  │ Verificaciones:                                            │  │
│  │   - Transacciones activas                                  │  │
│  │   - Órdenes pendientes                                     │  │
│  │   - Otras relaciones de negocio                            │  │
│  │                                                            │  │
│  │ → has_active_relations: bool                               │  │
│  └───────────────────────────────────────────────────────────┘  │
│                         │                                         │
│              ┌──────────┴──────────┐                             │
│              │                      │                             │
│     has_active = true      has_active = false                    │
│              │                      │                             │
│              ▼                      ▼                             │
│     ┌─────────────┐       ┌─────────────────┐                    │
│     │ SOFT DELETE │       │ INTENTAR HARD   │                    │
│     │ (paso 4b)   │       │ DELETE (paso 4a)│                    │
│     └─────────────┘       └─────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              4a. INTENTAR HARD DELETE (try-catch)                │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ try:                                                       │  │
│  │   _execute_hard_delete()                                   │  │
│  │     │                                                      │  │
│  │     ├─ 4a.1 Obtener todas las locations de la compañía    │  │
│  │     │       LocationListUseCase(company_id)               │  │
│  │     │                                                      │  │
│  │     ├─ 4a.2 Para cada location:                           │  │
│  │     │       Obtener user_location_rols                    │  │
│  │     │       Para cada ulr:                                │  │
│  │     │         Obtener user                                │  │
│  │     │         Eliminar ulr (UserLocationRolDelete)        │  │
│  │     │         Eliminar user (UserDelete)                  │  │
│  │     │         Eliminar platform (PlatformDelete)          │  │
│  │     │                                                      │  │
│  │     ├─ 4a.3 Obtener todos los menus de la compañía        │  │
│  │     │       MenuListUseCase(company_id)                   │  │
│  │     │                                                      │  │
│  │     ├─ 4a.4 Para cada menu:                               │  │
│  │     │       Eliminar menu_permissions                     │  │
│  │     │       Eliminar menu                                 │  │
│  │     │                                                      │  │
│  │     ├─ 4a.5 Eliminar todas las locations                  │  │
│  │     │       LocationDeleteUseCase(id)                     │  │
│  │     │                                                      │  │
│  │     └─ 4a.6 Eliminar company                              │  │
│  │             CompanyDeleteUseCase(id)                      │  │
│  │                                                            │  │
│  │ except Exception:                                          │  │
│  │   → Ir a SOFT DELETE (4b)                                  │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                 4b. SOFT DELETE (fallback)                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ SoftDeleteCompanyUseCase.execute(company)                  │  │
│  │                                                            │  │
│  │ CompanyUpdateUseCase({                                     │  │
│  │   id: company.id,                                          │  │
│  │   state: false  ← Inactivar compañía                       │  │
│  │ })                                                         │  │
│  │                                                            │  │
│  │ → Retornar mensaje: "Compañía inactivada, será eliminada   │  │
│  │                      permanentemente después de 1 mes"     │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    5. RESPUESTA                                   │
│                                                                   │
│  Hard Delete exitoso:                                             │
│  {                                                                │
│    "success": true,                                               │
│    "data": { "message": "Compañía eliminada exitosamente" },     │
│    "message": "Compañía eliminada exitosamente"                   │
│  }                                                                │
│                                                                   │
│  Soft Delete (fallback):                                          │
│  {                                                                │
│    "success": false,                                              │
│    "data": null,                                                  │
│    "message": "La compañía tiene relaciones activas..."          │
│  }                                                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Especificación Técnica

### Arquitectura del Flujo

```
Controller (Business)
    │
    ├── DeleteCompanyUseCase (Principal - auth/delete_company/)
    │   │
    │   ├── 1. Validaciones
    │   │   ├── CompanyReadUseCase (verificar existe)
    │   │   └── LocationReadUseCase (verificar admin pertenece)
    │   │
    │   ├── 2. CheckCompanyActiveRelationsUseCase (auxiliar)
    │   │
    │   ├── 3a. _execute_hard_delete() (método privado)
    │   │   ├── LocationListUseCase
    │   │   ├── UserLocationRolListUseCase
    │   │   ├── UserLocationRolDeleteUseCase (múltiples)
    │   │   ├── UserDeleteUseCase (múltiples)
    │   │   ├── PlatformDeleteUseCase (múltiples)
    │   │   ├── MenuListUseCase
    │   │   ├── MenuPermissionListUseCase
    │   │   ├── MenuPermissionDeleteUseCase (múltiples)
    │   │   ├── MenuDeleteUseCase (múltiples)
    │   │   ├── LocationDeleteUseCase (múltiples)
    │   │   └── CompanyDeleteUseCase
    │   │
    │   └── 3b. SoftDeleteCompanyUseCase (auxiliar - fallback)
    │       └── CompanyUpdateUseCase

Estructura de archivos:
src/domain/services/use_cases/business/auth/
├── delete_company/
│   ├── __init__.py
│   ├── delete_company_use_case.py (principal)
│   ├── check_company_active_relations_use_case.py (auxiliar)
│   └── soft_delete_company_use_case.py (auxiliar)
```

### Stack Tecnológico

- **Backend**: Python 3.11 + FastAPI
- **ORM**: SQLAlchemy (async)
- **Base de Datos**: PostgreSQL 14+
- **Validación**: Pydantic v2
- **Autenticación**: JWT

---

## Endpoints API

### DELETE /auth/delete-company/{company_id}

**Descripción**: Elimina una compañía del sistema

**Autenticación**: ✅ Requiere token JWT válido

**Permisos**: `DELETE`

**Roles**: `ADMIN`

**Path Parameters**:

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `company_id` | UUID | Sí | ID de la compañía a eliminar |

**Response 200 (Hard Delete Success)**:

```json
{
  "success": true,
  "data": {
    "message": "Compañía eliminada exitosamente"
  },
  "message": "Compañía eliminada exitosamente"
}
```

**Response 200 (Soft Delete - Error Controlado)**:

```json
{
  "success": false,
  "data": null,
  "message": "La compañía tiene relaciones activas y no pudo ser eliminada, pero fue inactivada. Será eliminada permanentemente después de 1 mes"
}
```

**Response 400 (Validation Error)**:

```json
{
  "success": false,
  "data": null,
  "message": "La compañía con ID {company_id} no existe en el sistema"
}
```

**Response 403 (Unauthorized)**:

```json
{
  "success": false,
  "data": null,
  "message": "No tiene autorización para eliminar esta compañía"
}
```

---

## Modelos de Datos

### Request Models

#### DeleteCompanyRequest

**Archivo**: `src/domain/models/business/auth/delete_company/delete_company_request.py`

```python
from pydantic import BaseModel, Field, UUID4


class DeleteCompanyRequest(BaseModel):
    company_id: UUID4 = Field(..., description="ID de la compañía a eliminar")

    class Config:
        json_schema_extra = {
            "example": {
                "company_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }
```

### Response Models

#### DeleteCompanyResponse

**Archivo**: `src/domain/models/business/auth/delete_company/delete_company_response.py`

```python
from pydantic import BaseModel, Field


class DeleteCompanyResponse(BaseModel):
    message: str = Field(...)
```

---

## Validaciones y Reglas

### Validaciones de Request

| Campo | Validación | Mensaje de Error |
|-------|-----------|------------------|
| `company_id` | Debe ser UUID válido | "ID de compañía inválido" |
| `company_id` | Compañía debe existir | "La compañía con ID {company_id} no existe" |

### Reglas de Negocio

1. **Admin de la Compañía**:
   ```python
   # Obtener location del admin desde el token
   admin_location_id = config.token.location_id
   
   # Verificar que la location pertenece a la compañía
   location = await self.location_read_uc.execute(
       config=config,
       params=LocationRead(id=admin_location_id)
   )
   
   if str(location.company_id) != str(params.company_id):
       return "No autorizado para eliminar esta compañía"
   ```

2. **Verificación de Relaciones Activas**:
   ```python
   # Extensible: agregar verificaciones de otras tablas
   # - Transacciones
   # - Órdenes
   # - Facturas
   # Por ahora retorna False (sin relaciones adicionales)
   ```

3. **Orden de Eliminación** (Hard Delete):
   - Primero: UserLocationRol (rompe relación user-location-rol)
   - Segundo: Users (elimina usuarios)
   - Tercero: Platform (configuración de cada usuario)
   - Cuarto: MenuPermissions (permisos de menús)
   - Quinto: Menus (menús de la compañía)
   - Sexto: Locations (ubicaciones)
   - Último: Company (la compañía)

4. **Soft Delete como Fallback**:
   ```python
   try:
       await self._execute_hard_delete(...)
       return None  # Éxito
   except Exception:
       # Cualquier error → soft delete
       return await self._handle_soft_delete(config, company)
   ```

---

## Casos de Uso Involucrados

### Use Cases de Validación (Read/List)

| Use Case | Propósito | Ejecuciones |
|----------|-----------|-------------|
| `CompanyReadUseCase` | Validar compañía existe | 1 vez |
| `LocationReadUseCase` | Validar admin pertenece | 1 vez |
| `LocationListUseCase` | Obtener todas las locations | 1 vez |
| `UserLocationRolListUseCase` | Obtener users por location | N veces |
| `MenuListUseCase` | Obtener menús de la compañía | 1 vez |
| `MenuPermissionListUseCase` | Obtener permisos por menú | M veces |

### Use Cases de Eliminación (Delete)

| Use Case | Propósito | Ejecuciones |
|----------|-----------|-------------|
| `UserLocationRolDeleteUseCase` | Eliminar relaciones user-location-rol | N veces |
| `UserDeleteUseCase` | Eliminar usuarios | N veces |
| `PlatformDeleteUseCase` | Eliminar platforms | N veces |
| `MenuPermissionDeleteUseCase` | Eliminar permisos de menú | M veces |
| `MenuDeleteUseCase` | Eliminar menús | K veces |
| `LocationDeleteUseCase` | Eliminar locations | L veces |
| `CompanyDeleteUseCase` | Eliminar compañía | 1 vez |

### Use Cases Auxiliares

| Use Case | Propósito | Ubicación |
|----------|-----------|-----------|
| `CheckCompanyActiveRelationsUseCase` | Verificar relaciones activas | `auth/delete_company/` |
| `SoftDeleteCompanyUseCase` | Inactivar compañía | `auth/delete_company/` |

---

## Manejo de Errores

### Códigos de Error y Traducciones

```sql
-- Errores de validación
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'delete_company_not_found', 'es', 'La compañía con ID {company_id} no existe en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'delete_company_not_found', 'en', 'The company with ID {company_id} does not exist in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'delete_company_unauthorized', 'es', 'No tiene autorización para eliminar esta compañía', 'backend', true, now(), now()),
(uuid_generate_v4(), 'delete_company_unauthorized', 'en', 'You are not authorized to delete this company', 'backend', true, now(), now()),

(uuid_generate_v4(), 'delete_company_has_active_relations', 'es', 'La compañía tiene relaciones activas y no puede ser eliminada', 'backend', true, now(), now()),
(uuid_generate_v4(), 'delete_company_has_active_relations', 'en', 'The company has active relations and cannot be deleted', 'backend', true, now(), now());

-- Errores de proceso
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'delete_company_error_deleting_users', 'es', 'Error al eliminar los usuarios de la compañía', 'backend', true, now(), now()),
(uuid_generate_v4(), 'delete_company_error_deleting_users', 'en', 'Error deleting company users', 'backend', true, now(), now()),

(uuid_generate_v4(), 'delete_company_error_deleting_menus', 'es', 'Error al eliminar los menús de la compañía', 'backend', true, now(), now()),
(uuid_generate_v4(), 'delete_company_error_deleting_menus', 'en', 'Error deleting company menus', 'backend', true, now(), now()),

(uuid_generate_v4(), 'delete_company_error_deleting_locations', 'es', 'Error al eliminar las ubicaciones de la compañía', 'backend', true, now(), now()),
(uuid_generate_v4(), 'delete_company_error_deleting_locations', 'en', 'Error deleting company locations', 'backend', true, now(), now()),

(uuid_generate_v4(), 'delete_company_error_deleting_company', 'es', 'Error al eliminar la compañía', 'backend', true, now(), now()),
(uuid_generate_v4(), 'delete_company_error_deleting_company', 'en', 'Error deleting company', 'backend', true, now(), now());

-- Soft delete (inactivación)
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'delete_company_soft_deleted', 'es', 'La compañía tiene relaciones activas y no pudo ser eliminada, pero fue inactivada. Será eliminada permanentemente después de 1 mes', 'backend', true, now(), now()),
(uuid_generate_v4(), 'delete_company_soft_deleted', 'en', 'The company has active relations and could not be deleted, but was deactivated. It will be permanently deleted after 1 month', 'backend', true, now(), now()),

(uuid_generate_v4(), 'delete_company_error_soft_delete', 'es', 'Error al inactivar la compañía', 'backend', true, now(), now()),
(uuid_generate_v4(), 'delete_company_error_soft_delete', 'en', 'Error deactivating company', 'backend', true, now(), now());

-- Éxito
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'delete_company_success', 'es', 'Compañía eliminada exitosamente', 'backend', true, now(), now()),
(uuid_generate_v4(), 'delete_company_success', 'en', 'Company deleted successfully', 'backend', true, now(), now());
```

---

## Seguridad

### Autenticación y Autorización

```python
@auth_router.delete(
    "/delete-company/{company_id}",
    status_code=status.HTTP_200_OK,
    response_model=Response[DeleteCompanyResponse]
)
@check_permissions([PERMISSION_TYPE.DELETE.value])
@check_roles([ROL_TYPE.ADMIN.value])
@execute_transaction_route(enabled=settings.has_track)
async def delete_company(
    company_id: UUID = Path(..., description="ID de la compañía a eliminar"),
    config: Config = Depends(get_config)
) -> Response[DeleteCompanyResponse]:
    return await auth_controller.delete_company(config=config, company_id=company_id)
```

### Validación de Pertenencia

El administrador debe pertenecer a una ubicación de la compañía que intenta eliminar:

```python
# Obtener location del admin desde el token
admin_location_id = config.token.location_id

# Obtener la location
location = await self.location_read_uc.execute(
    config=config,
    params=LocationRead(id=admin_location_id)
)

# Verificar que pertenece a la compañía
if str(location.company_id) != str(params.company_id):
    return await self.message.get_message(
        config=config,
        message=MessageCoreEntity(
            key=KEYS_MESSAGES.DELETE_COMPANY_UNAUTHORIZED.value
        ),
    )
```

---

## Ejemplos de Uso

### Ejemplo 1: Eliminación Exitosa (Hard Delete)

**Request**:

```bash
curl -X DELETE "https://api.goluti.com/auth/delete-company/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response 200**:

```json
{
  "success": true,
  "data": {
    "message": "Compañía eliminada exitosamente"
  },
  "message": "Compañía eliminada exitosamente"
}
```

### Ejemplo 2: Soft Delete (Tiene Relaciones Activas)

**Request**:

```bash
curl -X DELETE "https://api.goluti.com/auth/delete-company/660e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response 200**:

```json
{
  "success": false,
  "data": null,
  "message": "La compañía tiene relaciones activas y no pudo ser eliminada, pero fue inactivada. Será eliminada permanentemente después de 1 mes"
}
```

### Ejemplo 3: Error - No Autorizado

**Request** (admin de otra compañía):

```bash
curl -X DELETE "https://api.goluti.com/auth/delete-company/770e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response 400**:

```json
{
  "success": false,
  "data": null,
  "message": "No tiene autorización para eliminar esta compañía"
}
```

---

## Referencias

### Documentos Relacionados

- [07-05-create-company-flow.md](./07-05-create-company-flow.md) - Flujo de creación de compañías (flujo inverso)
- [07-08-delete-user-internal-flow.md](./07-08-delete-user-internal-flow.md) - Flujo de eliminación de usuarios internos
- [04-00-core-overview.md](../04-core-components/04-00-core-overview.md) - Enums ROL_TYPE, PERMISSION_TYPE

### Tablas de Base de Datos

- `company` - Datos de compañías
- `location` - Ubicaciones de compañías
- `menu` - Menús del sistema
- `menu_permission` - Permisos asociados a menús
- `user` - Usuarios del sistema
- `user_location_rol` - Asignación de roles por ubicación
- `platform` - Configuración de plataforma de usuarios

---

## Historial de Cambios

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0 | 2024-12-05 | Equipo Goluti | Versión inicial del documento |

---

**Fin del documento**


# Flujo de Creación de Compañía (Create Company)

**Versión**: 1.0  
**Fecha**: Noviembre 12, 2024  
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

El flujo de **Create Company** permite la creación completa de una nueva compañía en el sistema, incluyendo:
- Registro de la compañía
- Duplicación de menús globales (plantilla) con company_id específico
- Creación de permisos asociados a los menús
- Creación de ubicación principal
- Creación de usuario administrador inicial

Este endpoint es **público** (sin autenticación requerida) para permitir el **auto-registro** de nuevas compañías. Está diseñado para el proceso de onboarding inicial y garantiza que todas las estructuras necesarias se creen de forma atómica.

---

## Objetivo

Proporcionar un endpoint único que permita crear una compañía completa en el sistema, ejecutando las siguientes operaciones de manera atómica:

1. Crear registro de compañía
2. Clonar estructura de menús desde plantilla global (menús con `company_id = NULL`)
3. Mantener relaciones jerárquicas de menús (padre-hijo)
4. Copiar permisos de menús desde plantilla
5. Crear ubicación principal de la compañía
6. Crear usuario administrador inicial de la compañía

### Alcance

**En alcance:**
- Creación de compañía con datos básicos
- Clonación inteligente de menús manteniendo jerarquías
- Generación de nuevos UUIDs para menús clonados
- Mapeo correcto de relaciones padre-hijo (id/top_id)
- Clonación de permisos de menú
- Creación de ubicación principal
- Creación de usuario administrador usando flujo existente
- Validaciones de integridad referencial
- Transaccionalidad del proceso completo

**Fuera de alcance:**
- Configuración avanzada de la compañía (puede hacerse después)
- Múltiples ubicaciones en creación (solo la principal)
- Múltiples usuarios en creación (solo el admin inicial)
- Personalización de menús en creación (se usa plantilla estándar)

---

## Contexto de Negocio

### Problema que Resuelve

Actualmente, crear una nueva compañía requiere múltiples pasos manuales:
1. `POST /company` - Crear compañía
2. Manualmente clonar menús de otra compañía o crear desde cero
3. Manualmente crear permisos de menú
4. `POST /location` - Crear ubicación
5. `POST /auth/create-user-internal` - Crear usuario admin

Este flujo unifica todo en una sola operación atómica, garantizando:
- Consistencia de datos
- Estructura de menús estándar para todas las compañías
- Reducción de errores humanos
- Simplificación del onboarding de nuevas compañías

### Reglas de Negocio Importantes

1. **Plantilla Global de Menús**: Los menús con `company_id = NULL` sirven como plantilla. Todos los nuevos con estos menús pero con su propio `company_id`.

2. **Preservación de Jerarquías**: Los menús tienen relación padre-hijo mediante `id` y `top_id`:
   - **Menú Cabeza**: `id == top_id` (es su propio padre)
   - **Menú Hijo**: `top_id` apunta al `id` del padre
   - Al clonar, se deben mantener estas relaciones

3. **Ubicación Principal**: Cada compañía debe tener al menos una ubicación marcada como `main_location = true`

4. **Usuario Admin Inicial**: Cada compañía necesita al menos un usuario administrador asociado a la ubicación principal

### Beneficios Esperados

- ✅ Onboarding rápido de nuevas compañías (segundos vs minutos/horas)
- ✅ Estructura estándar garantizada para todas las compañías
- ✅ Reducción de errores en configuración inicial
- ✅ Atomicidad: todo o nada
- ✅ Escalabilidad: plantilla centralizada y fácil de mantener
- ✅ Flexibilidad: después de crear, cada compañía puede personalizar sus menús

---

## Actores Involucrados

| Actor | Rol | Responsabilidad |
|-------|-----|-----------------|
| **Usuario Público** | Interesado en registrar empresa | Proporcionar datos de la compañía y admin |
| **Sistema** | Automático | Validar datos, clonar menús, crear estructuras, generar IDs |

---

## Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────────┐
│                 Request POST /auth/create-company                │
│  {                                                               │
│    company: { name, nit, inactivity_time },                     │
│    location: { name, address, city, phone, email, country_id }, │
│    admin_user: {                                                │
│      email, password, first_name, last_name,                    │
│      language_id, currency_id, rol_id                           │
│    }                                                            │
│  }                                                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    1. VALIDACIONES PREVIAS                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ ✓ NIT único (no existe otra compañía con ese NIT)?        │  │
│  │ ✓ Email único (no existe usuario con ese email)?          │  │
│  │ ✓ Country existe?                                          │  │
│  │ ✓ Language existe?                                         │  │
│  │ ✓ Currency existe?                                         │  │
│  │ ✓ Rol existe?                                              │  │
│  │ ✓ Existen menús template (company_id = NULL)?             │  │
│  │ ✓ Password cumple requisitos?                             │  │
│  └───────────────────────────────────────────────────────────┘  │
│                         │                                         │
│                         ▼ Si todas pasan                          │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    2. CREAR COMPAÑÍA                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ CompanySaveUseCase.execute({                               │  │
│  │   name: string,                                            │  │
│  │   nit: string,                                             │  │
│  │   inactivity_time: int,                                    │  │
│  │   state: true                                              │  │
│  │ })                                                         │  │
│  │                                                            │  │
│  │ → company_id: UUID (generado)                              │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│        3. CONSULTAR MENÚS TEMPLATE (company_id = NULL)           │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ MenuListUseCase.execute({                                  │  │
│  │   filters: [{ field: "company_id", value: null }]         │  │
│  │ })                                                         │  │
│  │                                                            │  │
│  │ → template_menus: List[Menu]                               │  │
│  │                                                            │  │
│  │ Ejemplo de estructura:                                     │  │
│  │   CABEZA: Home (id: A, top_id: A)                          │  │
│  │   CABEZA: Citas (id: B, top_id: B)                         │  │
│  │     HIJO: Crear Cita (id: C, top_id: B) ← hijo de Citas   │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│      4. CLONAR MENÚS MANTENIENDO JERARQUÍAS                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ CloneMenusForCompanyUseCase.execute({                      │  │
│  │   company_id: UUID,                                        │  │
│  │   template_menus: List[Menu]                               │  │
│  │ })                                                         │  │
│  │                                                            │  │
│  │ Proceso:                                                   │  │
│  │ a) Crear mapeo: old_id → new_id para todos los menús      │  │
│  │    Ejemplo:                                                │  │
│  │    A (Home cabeza) → A' (nuevo UUID)                       │  │
│  │    B (Citas cabeza) → B' (nuevo UUID)                      │  │
│  │    C (Crear hijo) → C' (nuevo UUID)                        │  │
│  │                                                            │  │
│  │ b) Para cada menú template:                                │  │
│  │    - Generar nuevo UUID                                    │  │
│  │    - Si es CABEZA (id == top_id):                          │  │
│  │        new_id = nuevo UUID                                 │  │
│  │        new_top_id = nuevo UUID (mismo)                     │  │
│  │    - Si es HIJO (id != top_id):                            │  │
│  │        new_id = nuevo UUID                                 │  │
│  │        new_top_id = mapeo[old_top_id]                      │  │
│  │    - company_id = nuevo company_id                         │  │
│  │    - Guardar con MenuSaveUseCase                           │  │
│  │                                                            │  │
│  │ → cloned_menus: List[Menu]                                 │  │
│  │ → menu_mapping: Dict[old_id → new_id]                      │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│           5. CONSULTAR PERMISOS DE MENÚS TEMPLATE                │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Para cada menú template:                                   │  │
│  │   MenuPermissionListUseCase.execute({                      │  │
│  │     filters: [{ field: "menu_id", value: template_menu_id }]│ │
│  │   })                                                       │  │
│  │                                                            │  │
│  │ → template_permissions: Dict[old_menu_id → List[Permission]]│ │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              6. CREAR PERMISOS PARA MENÚS CLONADOS               │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Para cada menú clonado:                                    │  │
│  │   old_menu_id = obtener del mapeo inverso                  │  │
│  │   permissions = template_permissions[old_menu_id]          │  │
│  │                                                            │  │
│  │   Para cada permission:                                    │  │
│  │     MenuPermissionSaveUseCase.execute({                    │  │
│  │       menu_id: new_menu_id,                                │  │
│  │       permission_id: permission.id,                        │  │
│  │       state: true                                          │  │
│  │     })                                                     │  │
│  │                                                            │  │
│  │ → created_permissions: List[MenuPermission]                │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              7. CREAR UBICACIÓN PRINCIPAL                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ LocationSaveUseCase.execute({                              │  │
│  │   company_id: company_id,                                  │  │
│  │   country_id: country_id,                                  │  │
│  │   name: string,                                            │  │
│  │   address: string,                                         │  │
│  │   city: string,                                            │  │
│  │   phone: string,                                           │  │
│  │   email: string,                                           │  │
│  │   main_location: true,  ← Ubicación principal             │  │
│  │   state: true                                              │  │
│  │ })                                                         │  │
│  │                                                            │  │
│  │ → location_id: UUID (generado)                             │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│            8. CREAR USUARIO ADMINISTRADOR INICIAL                │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ CreateUserInternalUseCase.execute({                        │  │
│  │   language_id: UUID,                                       │  │
│  │   currency_id: UUID,                                       │  │
│  │   location_rol: [{                                         │  │
│  │     location_id: location_id (del paso 7),                 │  │
│  │     rol_id: UUID (rol admin)                               │  │
│  │   }],                                                      │  │
│  │   email: string,                                           │  │
│  │   password: string,                                        │  │
│  │   first_name: string,                                      │  │
│  │   last_name: string,                                       │  │
│  │   identification_type: string,                             │  │
│  │   identification_number: string,                           │  │
│  │   phone: string,                                           │  │
│  │   state: true                                              │  │
│  │ })                                                         │  │
│  │                                                            │  │
│  │ Esto crea:                                                 │  │
│  │   - Platform                                               │  │
│  │   - User                                                   │  │
│  │   - UserLocationRol                                        │  │
│  │                                                            │  │
│  │ → user_created: User                                       │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    9. RESPUESTA EXITOSA                          │
│  {                                                               │
│    "success": true,                                             │
│    "data": null,                                                │
│    "message": "Compañía creada exitosamente"                    │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Especificación Técnica

### Arquitectura del Flujo

```
Controller (Business)
    │
    ├── CreateCompanyUseCase (Principal - auth/)
    │   │
    │   ├── 1. Validaciones
    │   │   ├── CompanyListUseCase (validar NIT único)
    │   │   ├── UserListUseCase (validar email único)
    │   │   ├── CountryReadUseCase
    │   │   ├── LanguageReadUseCase
    │   │   ├── CurrencyReadUseCase
    │   │   └── RolReadUseCase
    │   │
    │   ├── 2. CompanySaveUseCase
    │   │
    │   ├── 3. MenuListUseCase (obtener templates)
    │   │
    │   ├── 4. CloneMenusForCompanyUseCase (auxiliar - mismo nivel auth/)
    │   │   └── MenuSaveUseCase (múltiples veces)
    │   │
    │   ├── 5. MenuPermissionListUseCase (obtener permisos template)
    │   │
    │   ├── 6. CloneMenuPermissionsForCompanyUseCase (auxiliar - mismo nivel auth/)
    │   │   └── MenuPermissionSaveUseCase (múltiples veces)
    │   │
    │   ├── 7. LocationSaveUseCase
    │   │
    │   └── 8. CreateUserInternalUseCase

Nota: Todos los casos de uso (CreateCompanyUseCase, CloneMenusForCompanyUseCase, 
CloneMenuPermissionsForCompanyUseCase) están DENTRO de la carpeta:
src/domain/services/use_cases/business/auth/create_company/
```

### Stack Tecnológico

- **Backend**: Python 3.11 + FastAPI
- **ORM**: SQLAlchemy (async)
- **Base de Datos**: PostgreSQL 14+
- **Validación**: Pydantic v2
- **Autenticación**: JWT (para validar super admin)

---

## Endpoints API

### POST /auth/create-company

**Descripción**: Crea una compañía completa con toda su estructura inicial

**Autenticación**: ❌ No requiere autenticación (Endpoint público)

**Content-Type**: `application/json`

**Request Body**:

```json
{
  "company": {
    "name": "Empresa Ejemplo S.A.S.",
    "nit": "900123456-7",
    "inactivity_time": 30
  },
  "location": {
    "country_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Sede Principal",
    "address": "Calle 123 #45-67",
    "city": "Bogotá",
    "phone": "+57 300 1234567",
    "email": "contacto@empresaejemplo.com"
  },
  "admin_user": {
    "email": "admin@empresaejemplo.com",
    "password": "SecureP@ssw0rd123!",
    "first_name": "Juan",
    "last_name": "Pérez",
    "identification_type": "CC",
    "identification_number": "1234567890",
    "phone": "+57 300 9876543",
    "language_id": "660e8400-e29b-41d4-a716-446655440000",
    "currency_id": "770e8400-e29b-41d4-a716-446655440000",
    "rol_id": "880e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Response 201 (Success)**:

```json
{
  "success": true,
  "data": null,
  "message": "Compañía creada exitosamente"
}
```

**Response 400 (Validation Error)**:

```json
{
  "success": false,
  "data": null,
  "message": "El NIT ya está registrado en el sistema"
}
```

**Response 429 (Too Many Requests)**:

```json
{
  "success": false,
  "data": null,
  "message": "Demasiadas solicitudes. Por favor intente más tarde."
}
```

**Response 500 (Server Error)**:

```json
{
  "success": false,
  "data": null,
  "message": "Error al crear la compañía. Todos los cambios han sido revertidos."
}
```

---

## Modelos de Datos

### Request Models

#### CreateCompanyRequest

**Archivo**: `src/domain/models/business/auth/create_company/create_company_request.py`

```python
from pydantic import BaseModel, Field, UUID4, EmailStr
from typing import Optional

class CompanyData(BaseModel):
    """Datos de la compañía a crear"""
    name: str = Field(..., min_length=3, max_length=255, description="Nombre de la compañía")
    nit: str = Field(..., min_length=5, max_length=255, description="NIT de la compañía")
    inactivity_time: int = Field(default=30, ge=1, le=1440, description="Tiempo de inactividad en minutos")

class LocationData(BaseModel):
    """Datos de la ubicación principal"""
    country_id: UUID4 = Field(..., description="ID del país")
    name: str = Field(..., min_length=3, max_length=255, description="Nombre de la ubicación")
    address: str = Field(..., min_length=5, description="Dirección completa")
    city: str = Field(..., min_length=2, max_length=100, description="Ciudad")
    phone: str = Field(..., min_length=7, max_length=20, description="Teléfono")
    email: EmailStr = Field(..., description="Email de contacto de la ubicación")

class AdminUserData(BaseModel):
    """Datos del usuario administrador inicial"""
    email: EmailStr = Field(..., description="Email del usuario (login)")
    password: str = Field(..., min_length=8, max_length=100, description="Contraseña")
    first_name: str = Field(..., min_length=2, max_length=100, description="Nombre(s)")
    last_name: str = Field(..., min_length=2, max_length=100, description="Apellido(s)")
    identification_type: str = Field(..., max_length=10, description="Tipo de identificación (CC, CE, etc)")
    identification_number: str = Field(..., min_length=5, max_length=50, description="Número de identificación")
    phone: str = Field(..., min_length=7, max_length=20, description="Teléfono")
    language_id: UUID4 = Field(..., description="ID del idioma preferido")
    currency_id: UUID4 = Field(..., description="ID de la moneda preferida")
    rol_id: UUID4 = Field(..., description="ID del rol (debe ser rol de administrador)")

class CreateCompanyRequest(BaseModel):
    """Request completo para crear una compañía"""
    company: CompanyData = Field(..., description="Datos de la compañía")
    location: LocationData = Field(..., description="Datos de la ubicación principal")
    admin_user: AdminUserData = Field(..., description="Datos del usuario administrador")
```

#### CreateCompanyResponse

**Nota**: Este flujo **no retorna objeto `data`**, solo el mensaje de éxito traducido.

El use case retornará directamente el mensaje traducido usando:
```python
return await self.message.get_message(
    config=config,
    message=MessageCoreEntity(
        key="create_company_success"
    ),
)
```

El controller usará `Response.success_temporary_message()` con `data=None`

### Modelos de Mapeo Interno

#### MenuCloneMapping

```python
from pydantic import BaseModel, UUID4
from typing import Dict

class MenuCloneMapping(BaseModel):
    """Mapeo de IDs antiguos a nuevos para clonación de menús"""
    old_to_new: Dict[UUID4, UUID4] = Field(default_factory=dict)
    new_to_old: Dict[UUID4, UUID4] = Field(default_factory=dict)
    
    def add_mapping(self, old_id: UUID4, new_id: UUID4):
        """Agregar un mapeo bidireccional"""
        self.old_to_new[old_id] = new_id
        self.new_to_old[new_id] = old_id
    
    def get_new_id(self, old_id: UUID4) -> UUID4:
        """Obtener nuevo ID a partir del antiguo"""
        return self.old_to_new.get(old_id)
    
    def get_old_id(self, new_id: UUID4) -> UUID4:
        """Obtener ID antiguo a partir del nuevo"""
        return self.new_to_old.get(new_id)
```

---

## Validaciones y Reglas

### Validaciones de Request

| Campo | Validación | Mensaje de Error |
|-------|-----------|------------------|
| `company.name` | Mínimo 3 caracteres, máximo 255 | "El nombre de la compañía debe tener entre 3 y 255 caracteres" |
| `company.nit` | Mínimo 5 caracteres, único en BD | "El NIT ya está registrado en el sistema" |
| `company.inactivity_time` | Entre 1 y 1440 minutos | "El tiempo de inactividad debe estar entre 1 y 1440 minutos" |
| `location.country_id` | Debe existir en BD | "El país especificado no existe" |
| `location.email` | Formato email válido | "Email de ubicación inválido" |
| `admin_user.email` | Formato email válido, único en BD | "El email ya está registrado en el sistema" |
| `admin_user.password` | Mínimo 8 caracteres, complejidad | "La contraseña no cumple los requisitos de seguridad" |
| `admin_user.language_id` | Debe existir en BD | "El idioma especificado no existe" |
| `admin_user.currency_id` | Debe existir en BD | "La moneda especificada no existe" |
| `admin_user.rol_id` | Debe existir en BD | "El rol especificado no existe" |

### Reglas de Negocio

1. **NIT Único**: No puede existir otra compañía con el mismo NIT
   ```python
   # Validación
   existing_companies = await company_list_uc.execute(
       config=config,
       params=Pagination(filters=[
           FilterManager(field="nit", value=params.company.nit, condition=CONDITION_TYPE.EQUALS)
       ])
   )
   if existing_companies and not isinstance(existing_companies, str):
       return "El NIT ya está registrado en el sistema"
   ```

2. **Email Único**: No puede existir otro usuario con el mismo email
   ```python
   # Validación
   existing_users = await user_list_uc.execute(
       config=config,
       params=Pagination(filters=[
           FilterManager(field="email", value=params.admin_user.email, condition=CONDITION_TYPE.EQUALS)
       ])
   )
   if existing_users and not isinstance(existing_users, str):
       return "El email ya está registrado en el sistema"
   ```

3. **Plantilla de Menús Existe**: Debe haber al menos un menú con `company_id = NULL`
   ```python
   # Validación
   template_menus = await menu_list_uc.execute(
       config=config,
       params=Pagination(filters=[
           FilterManager(field="company_id", value=None, condition=CONDITION_TYPE.IS_NULL)
       ], all_data=True)
   )
   if not template_menus or isinstance(template_menus, str):
       return "No existe plantilla de menús en el sistema"
   ```

4. **Preservación de Jerarquía de Menús**: Al clonar menús, se debe mantener:
   - Los menús cabeza (id == top_id) siguen siendo cabeza
   - Los menús hijos mantienen su relación con la cabeza correcta
   ```python
   # Ejemplo de lógica
   for template_menu in template_menus:
       new_id = uuid.uuid4()
       
       if template_menu.id == template_menu.top_id:
           # Es cabeza: top_id apunta a sí mismo
           new_top_id = new_id
       else:
           # Es hijo: top_id apunta al nuevo padre mapeado
           new_top_id = menu_mapping.get_new_id(template_menu.top_id)
       
       menu_mapping.add_mapping(template_menu.id, new_id)
   ```

5. **Ubicación Principal**: La primera ubicación de una compañía debe ser `main_location = true`

6. **Transaccionalidad**: Si cualquier paso falla, TODOS los cambios se revierten

---

## Casos de Uso Involucrados

### Use Cases de Validación (Read/List)

| Use Case | Propósito | Ejecuciones |
|----------|-----------|-------------|
| `CompanyListUseCase` | Validar NIT único | 1 vez |
| `UserListUseCase` | Validar email único | 1 vez |
| `CountryReadUseCase` | Validar país existe | 1 vez |
| `LanguageReadUseCase` | Validar idioma existe | 1 vez |
| `CurrencyReadUseCase` | Validar moneda existe | 1 vez |
| `RolReadUseCase` | Validar rol existe | 1 vez |
| `MenuListUseCase` | Obtener menús template | 1 vez |
| `MenuPermissionListUseCase` | Obtener permisos de cada menú template | N veces (por cada menú) |

### Use Cases de Creación (Save)

| Use Case | Propósito | Ejecuciones |
|----------|-----------|-------------|
| `CompanySaveUseCase` | Crear compañía | 1 vez |
| `MenuSaveUseCase` | Crear menú clonado | N veces (por cada menú template) |
| `MenuPermissionSaveUseCase` | Crear permiso clonado | M veces (por cada permiso de cada menú) |
| `LocationSaveUseCase` | Crear ubicación principal | 1 vez |
| `CreateUserInternalUseCase` | Crear usuario admin completo | 1 vez |

### Use Cases Especializados (Nuevos - en carpeta create_company/)

| Use Case | Propósito | Ejecuciones | Ubicación |
|----------|-----------|-------------|-----------|
| `CloneMenusForCompanyUseCase` | Clonar menús manteniendo jerarquías | 1 vez | `auth/create_company/clone_menus_for_company_use_case.py` |
| `CloneMenuPermissionsForCompanyUseCase` | Clonar permisos de menús | 1 vez | `auth/create_company/clone_menu_permissions_for_company_use_case.py` |

**Nota**: Estos casos de uso auxiliares están en la **misma carpeta** `create_company/` junto con el caso de uso principal.

---

## Use Cases

### Estructura de Archivos

```
src/domain/services/use_cases/business/auth/
├── create_company/
│   ├── create_company_use_case.py (principal)
│   ├── clone_menus_for_company_use_case.py (auxiliar)
│   ├── clone_menu_permissions_for_company_use_case.py (auxiliar)
│   └── __init__.py
├── create_user_internal/ (carpeta existente)
├── create_user_external/ (carpeta existente)
├── login/ (carpeta existente)
└── ...
```

**Importante**: Cada flujo tiene **su propia carpeta** con todos sus casos de uso relacionados.

---

## Use Case Principal: CreateCompanyUseCase

**Archivo**: `src/domain/services/use_cases/business/auth/create_company/create_company_use_case.py`

```python
import uuid
from typing import Union, Dict, List
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

from src.domain.models.business.auth.create_company.index import (
    CreateCompanyRequest
)
from src.domain.models.entities.company.index import CompanySave
from src.domain.models.entities.location.index import LocationSave
from src.domain.models.entities.menu.index import Menu, MenuSave
from src.domain.models.entities.menu_permission.index import MenuPermissionSave
from src.domain.models.business.auth.create_user_internal.index import (
    CreateUserInternalRequest,
    LocationRolItem
)

# Importar repositorios
from src.infrastructure.database.repositories.entities.company_repository import CompanyRepository
from src.infrastructure.database.repositories.entities.country_repository import CountryRepository
from src.infrastructure.database.repositories.entities.language_repository import LanguageRepository
from src.infrastructure.database.repositories.entities.currency_repository import CurrencyRepository
from src.infrastructure.database.repositories.entities.rol_repository import RolRepository
from src.infrastructure.database.repositories.entities.user_repository import UserRepository
from src.infrastructure.database.repositories.entities.menu_repository import MenuRepository
from src.infrastructure.database.repositories.entities.menu_permission_repository import MenuPermissionRepository
from src.infrastructure.database.repositories.entities.location_repository import LocationRepository

# Importar use cases
from src.domain.services.use_cases.entities.company.company_save_use_case import CompanySaveUseCase
from src.domain.services.use_cases.entities.company.company_list_use_case import CompanyListUseCase
from src.domain.services.use_cases.entities.country.country_read_use_case import CountryReadUseCase
from src.domain.services.use_cases.entities.language.language_read_use_case import LanguageReadUseCase
from src.domain.services.use_cases.entities.currency.currency_read_use_case import CurrencyReadUseCase
from src.domain.services.use_cases.entities.rol.rol_read_use_case import RolReadUseCase
from src.domain.services.use_cases.entities.user.user_list_use_case import UserListUseCase
from src.domain.services.use_cases.entities.menu.menu_list_use_case import MenuListUseCase
from src.domain.services.use_cases.entities.menu.menu_save_use_case import MenuSaveUseCase
from src.domain.services.use_cases.entities.menu_permission.menu_permission_list_use_case import MenuPermissionListUseCase
from src.domain.services.use_cases.entities.menu_permission.menu_permission_save_use_case import MenuPermissionSaveUseCase
from src.domain.services.use_cases.entities.location.location_save_use_case import LocationSaveUseCase
from src.domain.services.use_cases.business.auth.create_user_internal.create_user_internal_use_case import CreateUserInternalUseCase

# Importar casos de uso auxiliares (misma carpeta - imports relativos)
from .clone_menus_for_company_use_case import CloneMenusForCompanyUseCase
from .clone_menu_permissions_for_company_use_case import CloneMenuPermissionsForCompanyUseCase

# Instanciar repositorios
company_repository = CompanyRepository()
country_repository = CountryRepository()
language_repository = LanguageRepository()
currency_repository = CurrencyRepository()
rol_repository = RolRepository()
user_repository = UserRepository()
menu_repository = MenuRepository()
menu_permission_repository = MenuPermissionRepository()
location_repository = LocationRepository()


class CreateCompanyUseCase:
    """
    Use Case para crear una compañía completa en el sistema.
    
    Proceso:
    1. Validar todas las referencias (NIT, email, country, language, currency, rol, templates)
    2. Crear Company
    3. Clonar menús template manteniendo jerarquías
    4. Clonar permisos de menús
    5. Crear Location principal
    6. Crear User admin inicial
    7. Retornar resumen de creación
    """
    
    def __init__(self):
        # Use cases de validación
        self.company_list_uc = CompanyListUseCase(company_repository)
        self.country_read_uc = CountryReadUseCase(country_repository)
        self.language_read_uc = LanguageReadUseCase(language_repository)
        self.currency_read_uc = CurrencyReadUseCase(currency_repository)
        self.rol_read_uc = RolReadUseCase(rol_repository)
        self.user_list_uc = UserListUseCase(user_repository)
        self.menu_list_uc = MenuListUseCase(menu_repository)
        self.menu_permission_list_uc = MenuPermissionListUseCase(menu_permission_repository)
        
        # Use cases de creación
        self.company_save_uc = CompanySaveUseCase(company_repository)
        self.menu_save_uc = MenuSaveUseCase(menu_repository)
        self.menu_permission_save_uc = MenuPermissionSaveUseCase(menu_permission_repository)
        self.location_save_uc = LocationSaveUseCase(location_repository)
        self.create_user_internal_uc = CreateUserInternalUseCase()
        
        # Use cases auxiliares (misma carpeta)
        self.clone_menus_uc = CloneMenusForCompanyUseCase()
        self.clone_permissions_uc = CloneMenuPermissionsForCompanyUseCase()
        
        self.message = Message()
    
    @execute_transaction(layer=LAYER.D_S_U_B.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: CreateCompanyRequest,
    ) -> Union[str, None]:
        """
        Ejecuta el flujo completo de creación de compañía.
        
        Args:
            config: Configuración de la solicitud
            params: Datos de la compañía, ubicación y usuario admin
            
        Returns:
            Mensaje de éxito o error traducido (string)
        """
        config.response_type = RESPONSE_TYPE.OBJECT
        
        # ============================================
        # 1. VALIDACIONES PREVIAS
        # ============================================
        
        # Validar NIT único
        existing_companies = await self.company_list_uc.execute(
            config=config,
            params=Pagination(filters=[
                FilterManager(
                    field="nit",
                    value=params.company.nit,
                    condition=CONDITION_TYPE.EQUALS
                )
            ])
        )
        if existing_companies and not isinstance(existing_companies, str):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key="create_company_nit_already_exists"
                ),
            )
        
        # Validar email único
        existing_users = await self.user_list_uc.execute(
            config=config,
            params=Pagination(filters=[
                FilterManager(
                    field="email",
                    value=params.admin_user.email,
                    condition=CONDITION_TYPE.EQUALS
                )
            ])
        )
        if existing_users and not isinstance(existing_users, str):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key="create_company_email_already_exists"
                ),
            )
        
        # Validar country existe
        country = await self.country_read_uc.execute(
            config=config,
            params={"id": params.location.country_id}
        )
        if isinstance(country, str):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key="create_company_country_not_found"
                ),
            )
        
        # Validar language existe
        language = await self.language_read_uc.execute(
            config=config,
            params={"id": params.admin_user.language_id}
        )
        if isinstance(language, str):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key="create_company_language_not_found"
                ),
            )
        
        # Validar currency existe
        currency = await self.currency_read_uc.execute(
            config=config,
            params={"id": params.admin_user.currency_id}
        )
        if isinstance(currency, str):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key="create_company_currency_not_found"
                ),
            )
        
        # Validar rol existe
        rol = await self.rol_read_uc.execute(
            config=config,
            params={"id": params.admin_user.rol_id}
        )
        if isinstance(rol, str):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key="create_company_rol_not_found"
                ),
            )
        
        # Validar que existan menús template (company_id = NULL)
        template_menus = await self.menu_list_uc.execute(
            config=config,
            params=Pagination(
                filters=[
                    FilterManager(
                        field="company_id",
                        value=None,
                        condition=CONDITION_TYPE.IS_NULL
                    )
                ],
                all_data=True
            )
        )
        if not template_menus or isinstance(template_menus, str):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key="create_company_no_menu_templates"
                ),
            )
        
        # ============================================
        # 2. CREAR COMPAÑÍA
        # ============================================
        
        company = await self.company_save_uc.execute(
            config=config,
            params=CompanySave(
                name=params.company.name,
                nit=params.company.nit,
                inactivity_time=params.company.inactivity_time,
                state=True
            )
        )
        
        if isinstance(company, str):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_ERROR_SAVING_RECORD.value
                ),
            )
        
        # ============================================
        # 3. CLONAR MENÚS MANTENIENDO JERARQUÍAS
        # ============================================
        
        # Usar caso de uso auxiliar para clonar menús
        clone_result = await self.clone_menus_uc.execute(
            config=config,
            company_id=company.id,
            template_menus=template_menus
        )
        
        if isinstance(clone_result, str):
            return clone_result  # Error en clonación
        
        cloned_menus, menu_mapping = clone_result
        
        # ============================================
        # 4. CLONAR PERMISOS DE MENÚS
        # ============================================
        
        # Usar caso de uso auxiliar para clonar permisos
        permissions_result = await self.clone_permissions_uc.execute(
            config=config,
            cloned_menus=cloned_menus,
            menu_mapping=menu_mapping
        )
        
        if isinstance(permissions_result, str):
            return permissions_result  # Error en clonación de permisos
        
        permissions_created = permissions_result
        
        # ============================================
        # 5. CREAR UBICACIÓN PRINCIPAL
        # ============================================
        
        location = await self.location_save_uc.execute(
            config=config,
            params=LocationSave(
                company_id=company.id,
                country_id=params.location.country_id,
                name=params.location.name,
                address=params.location.address,
                city=params.location.city,
                phone=params.location.phone,
                email=params.location.email,
                main_location=True,
                state=True
            )
        )
        
        if isinstance(location, str):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key="create_company_error_creating_location"
                ),
            )
        
        # ============================================
        # 6. CREAR USUARIO ADMINISTRADOR INICIAL
        # ============================================
        
        user_result = await self.create_user_internal_uc.execute(
            config=config,
            params=CreateUserInternalRequest(
                language_id=params.admin_user.language_id,
                currency_id=params.admin_user.currency_id,
                location_rol=[
                    LocationRolItem(
                        location_id=location.id,
                        rol_id=params.admin_user.rol_id
                    )
                ],
                email=params.admin_user.email,
                password=params.admin_user.password,
                first_name=params.admin_user.first_name,
                last_name=params.admin_user.last_name,
                identification_type=params.admin_user.identification_type,
                identification_number=params.admin_user.identification_number,
                phone=params.admin_user.phone,
                state=True
            )
        )
        
        if isinstance(user_result, str):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key="create_company_error_creating_admin"
                ),
            )
        
        # ============================================
        # 7. RETORNAR MENSAJE DE ÉXITO
        # ============================================
        
        return await self.message.get_message(
            config=config,
            message=MessageCoreEntity(
                key="create_company_success"
            ),
        )
```

---

## Use Cases Auxiliares

### CloneMenusForCompanyUseCase

**Archivo**: `src/domain/services/use_cases/business/auth/create_company/clone_menus_for_company_use_case.py`

**Responsabilidad**: Clonar menús template manteniendo las jerarquías padre-hijo.

```python
import uuid
from typing import Union, Dict, List, Tuple
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.wrappers.execute_transaction import execute_transaction
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from pydantic import UUID4

from src.domain.models.entities.menu.index import Menu, MenuSave
from src.domain.services.use_cases.entities.menu.menu_save_use_case import MenuSaveUseCase
from src.infrastructure.database.repositories.entities.menu_repository import MenuRepository

menu_repository = MenuRepository()


class CloneMenusForCompanyUseCase:
    """
    Caso de uso auxiliar para clonar menús manteniendo jerarquías.
    
    Proceso:
    1. Crear mapeo de IDs antiguos a nuevos (primera pasada)
    2. Crear menús preservando relaciones padre-hijo (segunda pasada)
    3. Retornar menús clonados y mapeo de IDs
    """
    
    def __init__(self):
        self.menu_save_uc = MenuSaveUseCase(menu_repository)
        self.message = Message()
    
    @execute_transaction(layer=LAYER.D_S_U_B.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        company_id: UUID4,
        template_menus: List[Menu]
    ) -> Union[Tuple[List[Menu], Dict[str, str]], str]:
        """
        Clona menús manteniendo jerarquías.
        
        Args:
            config: Configuración de la solicitud
            company_id: ID de la compañía para asociar los menús
            template_menus: Lista de menús template a clonar
            
        Returns:
            Tupla (menús_clonados, mapeo_ids) o mensaje de error
        """
        config.response_type = RESPONSE_TYPE.OBJECT
        
        # Crear mapeo de IDs antiguos a nuevos
        menu_mapping: Dict[str, str] = {}  # old_id -> new_id
        cloned_menus: List[Menu] = []
        
        # Primera pasada: generar todos los nuevos IDs
        for template_menu in template_menus:
            new_id = str(uuid.uuid4())
            menu_mapping[str(template_menu.id)] = new_id
        
        # Segunda pasada: crear los menús con las relaciones correctas
        for template_menu in template_menus:
            new_id = menu_mapping[str(template_menu.id)]
            
            # Determinar el nuevo top_id según la jerarquía
            if str(template_menu.id) == str(template_menu.top_id):
                # Es cabeza: top_id apunta a sí mismo
                new_top_id = new_id
            else:
                # Es hijo: top_id apunta al nuevo padre mapeado
                new_top_id = menu_mapping[str(template_menu.top_id)]
            
            # Crear el menú clonado
            cloned_menu = await self.menu_save_uc.execute(
                config=config,
                params=MenuSave(
                    company_id=company_id,
                    name=template_menu.name,
                    label=template_menu.label,
                    description=template_menu.description,
                    top_id=new_top_id,
                    route=template_menu.route,
                    state=template_menu.state,
                    icon=template_menu.icon
                )
            )
            
            if isinstance(cloned_menu, str):
                return await self.message.get_message(
                    config=config,
                    message=MessageCoreEntity(
                        key="create_company_error_cloning_menus"
                    ),
                )
            
            cloned_menus.append(cloned_menu)
        
        return (cloned_menus, menu_mapping)
```

---

### CloneMenuPermissionsForCompanyUseCase

**Archivo**: `src/domain/services/use_cases/business/auth/create_company/clone_menu_permissions_for_company_use_case.py`

**Responsabilidad**: Clonar permisos de menús template a los menús clonados.

```python
from typing import Union, Dict, List
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination, FilterManager
from src.core.enums.condition_type import CONDITION_TYPE
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.wrappers.execute_transaction import execute_transaction
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity

from src.domain.models.entities.menu.index import Menu
from src.domain.models.entities.menu_permission.index import MenuPermissionSave
from src.domain.services.use_cases.entities.menu_permission.menu_permission_list_use_case import MenuPermissionListUseCase
from src.domain.services.use_cases.entities.menu_permission.menu_permission_save_use_case import MenuPermissionSaveUseCase
from src.infrastructure.database.repositories.entities.menu_permission_repository import MenuPermissionRepository

menu_permission_repository = MenuPermissionRepository()


class CloneMenuPermissionsForCompanyUseCase:
    """
    Caso de uso auxiliar para clonar permisos de menús.
    
    Proceso:
    1. Para cada menú clonado, obtener su ID original
    2. Consultar permisos del menú template
    3. Crear los mismos permisos para el menú clonado
    4. Retornar cantidad de permisos creados
    """
    
    def __init__(self):
        self.menu_permission_list_uc = MenuPermissionListUseCase(menu_permission_repository)
        self.menu_permission_save_uc = MenuPermissionSaveUseCase(menu_permission_repository)
        self.message = Message()
    
    @execute_transaction(layer=LAYER.D_S_U_B.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        cloned_menus: List[Menu],
        menu_mapping: Dict[str, str]
    ) -> Union[int, str]:
        """
        Clona permisos de menús template.
        
        Args:
            config: Configuración de la solicitud
            cloned_menus: Lista de menús clonados
            menu_mapping: Mapeo de IDs (old_id -> new_id)
            
        Returns:
            Cantidad de permisos creados o mensaje de error
        """
        config.response_type = RESPONSE_TYPE.OBJECT
        
        permissions_created = 0
        
        for cloned_menu in cloned_menus:
            # Obtener el ID original del menú
            original_menu_id = None
            for old_id, new_id in menu_mapping.items():
                if str(cloned_menu.id) == new_id:
                    original_menu_id = old_id
                    break
            
            if not original_menu_id:
                continue
            
            # Obtener permisos del menú template
            template_permissions = await self.menu_permission_list_uc.execute(
                config=config,
                params=Pagination(
                    filters=[
                        FilterManager(
                            field="menu_id",
                            value=original_menu_id,
                            condition=CONDITION_TYPE.EQUALS
                        )
                    ],
                    all_data=True
                )
            )
            
            if template_permissions and not isinstance(template_permissions, str):
                # Crear los permisos para el menú clonado
                for template_permission in template_permissions:
                    cloned_permission = await self.menu_permission_save_uc.execute(
                        config=config,
                        params=MenuPermissionSave(
                            menu_id=cloned_menu.id,
                            permission_id=template_permission.permission_id,
                            state=template_permission.state
                        )
                    )
                    
                    if not isinstance(cloned_permission, str):
                        permissions_created += 1
        
        return permissions_created
```

---

## Controller

**Archivo**: `src/infrastructure/web/controller/business/auth_controller.py`

```python
from src.core.models.response import Response
from src.core.models.config import Config
from src.domain.models.business.auth.create_company.index import CreateCompanyRequest
from src.domain.services.use_cases.business.auth.create_company.create_company_use_case import CreateCompanyUseCase

class AuthController:
    def __init__(self):
        self.create_company_uc = CreateCompanyUseCase()
    
    @execute_transaction(layer=LAYER.I_W_C_B.value, enabled=settings.has_track)
    async def create_company(
        self, 
        config: Config, 
        params: CreateCompanyRequest
    ) -> Response:
        """
        Controller para crear una compañía completa.
        
        Returns:
            Response con data=None y mensaje de éxito o error
        """
        result = await self.create_company_uc.execute(
            config=config, 
            params=params
        )
        
        # result es siempre un string (mensaje traducido)
        if isinstance(result, str):
            # Si es un mensaje de error (no contiene "exitosamente" o "successfully")
            if "exitosamente" not in result.lower() and "successfully" not in result.lower():
                return Response.error(response=None, message=result)
            
            # Si es mensaje de éxito
            return Response.success_temporary_message(
                response=None,  # No se retorna data
                message=result
            )
        
        # Caso edge (no debería ocurrir)
        return Response.error(
            response=None, 
            message="Error inesperado al crear la compañía"
        )
```

**Router**: `src/infrastructure/web/business_routes/auth_router.py`

```python
@auth_router.post(
    "/create-company",
    response_model=Response,
    status_code=status.HTTP_201_CREATED,
    summary="Crear compañía completa (público)",
    description="Endpoint público para auto-registro de nuevas compañías"
)
async def create_company(
    params: CreateCompanyRequest,
    config: Config = Depends(get_config)
) -> Response:
    """
    Crea una compañía completa con toda su estructura inicial.
    
    - **Sin autenticación requerida**
    - Endpoint público
    - Retorna solo mensaje de éxito, sin data
    """
    return await auth_controller.create_company(config=config, params=params)
```

---

## Manejo de Errores

### Códigos de Error y Traducciones

Agregar a la tabla `translation`:

```sql
-- Errores de validación
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'create_company_nit_already_exists', 'es', 'El NIT ya está registrado en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'create_company_nit_already_exists', 'en', 'The NIT is already registered in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'create_company_email_already_exists', 'es', 'El email ya está registrado en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'create_company_email_already_exists', 'en', 'The email is already registered in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'create_company_country_not_found', 'es', 'El país especificado no existe en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'create_company_country_not_found', 'en', 'The specified country does not exist in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'create_company_language_not_found', 'es', 'El idioma especificado no existe en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'create_company_language_not_found', 'en', 'The specified language does not exist in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'create_company_currency_not_found', 'es', 'La moneda especificada no existe en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'create_company_currency_not_found', 'en', 'The specified currency does not exist in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'create_company_rol_not_found', 'es', 'El rol especificado no existe en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'create_company_rol_not_found', 'en', 'The specified role does not exist in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'create_company_no_menu_templates', 'es', 'No existe plantilla de menús en el sistema. Contacte al administrador.', 'backend', true, now(), now()),
(uuid_generate_v4(), 'create_company_no_menu_templates', 'en', 'No menu templates exist in the system. Contact the administrator.', 'backend', true, now(), now()),

-- Errores de proceso
(uuid_generate_v4(), 'create_company_error_cloning_menus', 'es', 'Error al clonar los menús. Todos los cambios han sido revertidos.', 'backend', true, now(), now()),
(uuid_generate_v4(), 'create_company_error_cloning_menus', 'en', 'Error cloning menus. All changes have been rolled back.', 'backend', true, now(), now()),

(uuid_generate_v4(), 'create_company_error_creating_location', 'es', 'Error al crear la ubicación. Todos los cambios han sido revertidos.', 'backend', true, now(), now()),
(uuid_generate_v4(), 'create_company_error_creating_location', 'en', 'Error creating location. All changes have been rolled back.', 'backend', true, now(), now()),

(uuid_generate_v4(), 'create_company_error_creating_admin', 'es', 'Error al crear el usuario administrador. Todos los cambios han sido revertidos.', 'backend', true, now(), now()),
(uuid_generate_v4(), 'create_company_error_creating_admin', 'en', 'Error creating admin user. All changes have been rolled back.', 'backend', true, now(), now()),

-- Éxito
(uuid_generate_v4(), 'create_company_success', 'es', 'Compañía creada exitosamente', 'backend', true, now(), now()),
(uuid_generate_v4(), 'create_company_success', 'en', 'Company created successfully', 'backend', true, now(), now()),

-- reCAPTCHA (Opcional)
(uuid_generate_v4(), 'create_company_recaptcha_failed', 'es', 'Verificación de seguridad fallida. Por favor intente nuevamente.', 'backend', true, now(), now()),
(uuid_generate_v4(), 'create_company_recaptcha_failed', 'en', 'Security verification failed. Please try again.', 'backend', true, now(), now());
```

### Estrategia de Rollback

Dado que el use case usa el decorador `@execute_transaction`, **toda la operación es atómica**:

- Si cualquier paso falla, PostgreSQL automáticamente hace rollback de TODOS los cambios
- No se necesita manejo manual de rollback
- Garantiza consistencia total de datos

---

## Seguridad

### Endpoint Público

Este endpoint **NO requiere autenticación** ya que está diseñado para el auto-registro de nuevas compañías.

```python
# En el router
@auth_router.post(
    "/create-company",
    response_model=Response,
    status_code=status.HTTP_201_CREATED,
    summary="Crear compañía completa (público)"
)
async def create_company(
    params: CreateCompanyRequest,
    config: Config = Depends(get_config)
    # Sin dependencia de autenticación - endpoint público
) -> Response:
    return await auth_controller.create_company(config=config, params=params)
```

### Medidas de Seguridad Implementadas

#### 1. Validación Estricta de Datos
- **NIT único**: Previene registro duplicado
- **Email único**: Previene múltiples registros con mismo email
- **Password fuerte**: Mínimo 8 caracteres, complejidad requerida
- **Formato de datos**: Validación exhaustiva con Pydantic
- **Transacciones atómicas**: Si algo falla, todo se revierte

#### 2. Protección contra Spam/Bots (Opcional - Recomendada)

**Opción A: reCAPTCHA**
```python
from src.core.security.recaptcha import verify_recaptcha

@auth_router.post("/create-company")
async def create_company(
    params: CreateCompanyRequest,
    recaptcha_token: str = Body(..., embed=True),
    config: Config = Depends(get_config)
):
    # Verificar reCAPTCHA
    if not await verify_recaptcha(recaptcha_token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verificación de reCAPTCHA fallida"
        )
    
    return await auth_controller.create_company(config=config, params=params)
```

**Opción B: Verificación por Email**
- Enviar email de confirmación al admin_user.email
- La compañía se crea pero inactiva (`state = false`)
- Activar solo después de confirmar email

**Opción C: Proceso de Aprobación Manual**
- Crear compañía en estado "pendiente de aprobación"
- Super admin debe aprobar manualmente
- Enviar notificación al equipo interno

#### 3. Protección de Datos Sensibles
- **Password**: Se hashea usando bcrypt antes de guardar
- **Logs**: No registrar passwords en logs
- **HTTPS**: Obligatorio en producción
- **No se devuelve password** en ninguna respuesta

#### 4. Validación de Integridad
- Verificar que referencias existen (country, language, currency, rol)
- Verificar formato de email
- Verificar formato de teléfono
- Verificar que existen menús template

#### 5. Auditoría (Opcional - Recomendada)
```python
# Registrar cada intento de creación de compañía
audit_log = {
    "action": "create_company_attempt",
    "ip_address": request.client.host,
    "nit": params.company.nit,
    "email": params.admin_user.email,
    "timestamp": datetime.now(),
    "success": result_success
}
```

### Recomendaciones de Seguridad Futuras

> **Nota**: Estas medidas NO están implementadas actualmente pero son recomendadas para producción.

#### 1. Rate Limiting
**Pendiente de definir e implementar**

Estrategias recomendadas:
- **Por IP**: Limitar intentos por dirección IP (ej: 3-5 intentos/hora)
- **Por NIT**: Prevenir múltiples intentos con mismo NIT
- **Por Email**: Prevenir múltiples intentos con mismo email
- **Global**: Alertar si hay picos anormales de creación

Opciones de implementación:
- Extender `UserRateLimitMiddleware` existente
- Usar Redis para rate limiting distribuido
- Implementar en WAF/API Gateway (Cloudflare, AWS WAF, etc.)

#### 2. Monitoreo y Alertas
- Alertar si más de X compañías se crean en Y minutos
- Detectar patrones sospechosos (mismo formato de datos, IPs secuenciales, etc.)
- Dashboard de métricas de registro

#### 3. Validación Avanzada de Email
- Blacklist de dominios de email temporales
- Validar que el dominio tenga registro MX válido
- Verificación por email antes de activar compañía

#### 4. Validación de NIT
   - Opcional: validar formato de NIT según país
   - Opcional: consultar API externa para verificar NIT real

### Riesgos y Mitigación

| Riesgo | Impacto | Mitigación Actual | Mitigación Futura |
|--------|---------|-------------------|-------------------|
| Registro masivo automatizado | Alto | Validación de datos + transacciones | Rate limiting + reCAPTCHA |
| Datos falsos/spam | Medio | NIT único + email único | Verificación email + validación NIT externa |
| Abuso de recursos (menús) | Bajo | Plantilla template controlada | Límite por hora + monitoreo |
| Sobrecarga de BD | Medio | Transacciones optimizadas | Rate limiting + cache + monitoreo |

---

## Ejemplos de Uso

### Ejemplo 1: Creación Exitosa

**Request**:

```bash
curl -X POST "https://api.goluti.com/auth/create-company" \
  -H "Content-Type: application/json" \
  -d '{
    "company": {
      "name": "TechStart S.A.S.",
      "nit": "900555666-1",
      "inactivity_time": 30
    },
    "location": {
      "country_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Sede Principal Bogotá",
      "address": "Calle 100 #15-20 Oficina 501",
      "city": "Bogotá",
      "phone": "+57 601 7654321",
      "email": "info@techstart.com"
    },
    "admin_user": {
      "email": "admin@techstart.com",
      "password": "TechStart2024!Secure",
      "first_name": "María",
      "last_name": "González",
      "identification_type": "CC",
      "identification_number": "1234567890",
      "phone": "+57 300 1234567",
      "language_id": "660e8400-e29b-41d4-a716-446655440000",
      "currency_id": "770e8400-e29b-41d4-a716-446655440000",
      "rol_id": "880e8400-e29b-41d4-a716-446655440000"
    }
  }'
```

**Response 201**:

```json
{
  "success": true,
  "data": null,
  "message": "Compañía creada exitosamente"
}
```

### Ejemplo 2: NIT Duplicado (Error 400)

**Request**:

```bash
curl -X POST "https://api.goluti.com/auth/create-company" \
  -H "Content-Type: application/json" \
  -d '{
    "company": {
      "name": "Otra Empresa",
      "nit": "900555666-1",
      "inactivity_time": 30
    },
    ...
  }'
```

**Response 400**:

```json
{
  "success": false,
  "data": null,
  "message": "El NIT ya está registrado en el sistema"
}
```

### Ejemplo 3: Con reCAPTCHA (Si se implementa)

**Request**:

```bash
curl -X POST "https://api.goluti.com/auth/create-company" \
  -H "Content-Type: application/json" \
  -d '{
    "recaptcha_token": "03AGdBq26...",
    "company": {
      "name": "TechStart S.A.S.",
      ...
    },
    ...
  }'
```

---

## Referencias

### Documentos Relacionados

- [07-01-create-user-internal-flow.md](./07-01-create-user-internal-flow.md) - Flujo de creación de usuarios internos (usado en paso 6)
- [02-entity-flow-overview.md](../02-entity-flow/02-00-entity-flow-overview.md) - Patrón Entity Flow
- [03-business-flow-overview.md](../03-business-flow/03-00-business-flow-overview.md) - Patrón Business Flow
- Changelog v28: Script para hacer `company_id` opcional en tabla `menu`
- Changelog v29: Script para insertar menús globales (plantilla)

### Tablas de Base de Datos

- `company` - Datos de compañías
- `menu` - Menús del sistema (con `company_id` opcional)
- `menu_permission` - Permisos asociados a menús
- `location` - Ubicaciones de compañías
- `platform` - Configuración de plataforma de usuarios
- `user` - Usuarios del sistema
- `user_location_rol` - Asignación de roles por ubicación

### APIs Externas

Ninguna. Este flujo es completamente interno.

---

## Historial de Cambios

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0 | 2024-11-12 | Equipo Goluti | Versión inicial del documento |

---

## Notas de Implementación

### Orden de Implementación Sugerido

1. **Fase 1**: Crear modelos de request
   - `CreateCompanyRequest`
   - `CompanyData`, `LocationData`, `AdminUserData`
   - Ubicación: `src/domain/models/business/auth/create_company/`

2. **Fase 2**: Agregar traducciones a la BD
   - Ejecutar script SQL con todas las keys de traducción

3. **Fase 3**: Crear carpeta y casos de uso auxiliares
   - Crear carpeta: `src/domain/services/use_cases/business/auth/create_company/`
   - Implementar `clone_menus_for_company_use_case.py`
   - Implementar `clone_menu_permissions_for_company_use_case.py`
   - Estos son helpers que encapsulan lógica específica

4. **Fase 4**: Implementar caso de uso principal
   - Implementar `create_company_use_case.py` en la misma carpeta
   - Empezar con validaciones
   - Agregar creación de company y location
   - Llamar a casos de uso auxiliares para clonar menús y permisos
   - Integrar creación de usuario (reutilizar CreateUserInternalUseCase)

5. **Fase 5**: Crear controller y router
   - `AuthController.create_company()`
   - Router POST `/auth/create-company`
   - Sin autenticación (público)

6. **Fase 6**: Testing
   - Unit tests para cada caso de uso (principal + auxiliares)
   - Integration test del flujo completo
   - Test de rollback (simulando fallas)
   - Test de validaciones (NIT único, email único, etc.)

### Consideraciones de Performance

- **Clonación de menús**: Si hay muchos menús template (>100), considerar procesamiento en batch
- **Transaccionalidad**: El proceso completo puede tomar 5-10 segundos. Comunicar esto al frontend.
- **Timeout**: Configurar timeout adecuado en el endpoint (30+ segundos)

### Mejoras Futuras

#### Seguridad
- **Rate Limiting**: Limitar intentos por IP, NIT y email (ver sección "Recomendaciones de Seguridad Futuras")
- **reCAPTCHA v3**: Verificación invisible sin fricción para el usuario
- **Validación de NIT Real**: Integración con APIs gubernamentales para validar NIT
- **Verificación de Teléfono**: SMS de verificación adicional

#### Funcionalidad
- **Async Jobs**: Para compañías muy grandes, mover clonación a job asíncrono
- **Personalización**: Permitir seleccionar qué menús clonar
- **Verificación por Email**: Email de confirmación antes de activar compañía
- **Notificaciones**: Enviar email de bienvenida al admin creado
- **Aprobación Manual**: Proceso de revisión por super admin antes de activar
- **Límites por País/Región**: Diferentes políticas según el mercado

#### Monitoreo
- **Audit Log Detallado**: Registrar IP, timestamp, y datos de cada intento de creación
- **Dashboard de Métricas**: Visualizar registros por día/hora, tasa de éxito, etc.
- **Alertas Automáticas**: Notificar picos anormales de registro

---

**Fin del documento**


# 07-12: Flujo de Autenticación (Login) con Orquestador

## Información del Documento

| Campo | Detalle |
|-------|---------|
| **Versión** | 2.6 |
| **Última Actualización** | Enero 23, 2026 |
| **Autor** | Equipo de Desarrollo Goluti |
| **Estado** | Activo |

---

## Resumen Ejecutivo

Este documento especifica el flujo de autenticación (login) del sistema con soporte para **usuarios internos** (ADMIN, COLLA) y **usuarios externos** (USER). El endpoint único `/auth/login` utiliza un **caso de uso orquestador** que detecta automáticamente el tipo de usuario y redirige al flujo correspondiente.

**Características principales:**
- ✅ Un único endpoint para todos los tipos de usuario
- ✅ Detección automática del tipo de usuario **basada en el rol** (marca irrefutable)
- ✅ Flujo completo para usuarios internos (con company, location, rol ADMIN/COLLA)
- ✅ Flujo simplificado para usuarios externos (sin company ni location, rol USER)
- ✅ Todos los usuarios registrados en `user_location_rol` (externos con `location_id = NULL`)
- ✅ Generación de tokens JWT personalizados según tipo de usuario
- ✅ Arquitectura basada en orquestador para mejor mantenibilidad
- ✅ Campo `type` en tabla `menu` para seguridad y filtrado (INTERNAL/EXTERNAL)

---

## Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Arquitectura del Orquestador](#arquitectura-del-orquestador)
3. [Endpoint](#endpoint)
4. [Diagrama de Flujo](#diagrama-de-flujo)
5. [Modelos de Datos](#modelos-de-datos)
6. [Casos de Uso](#casos-de-uso)
7. [Flujo de Usuario Interno](#flujo-de-usuario-interno)
8. [Flujo de Usuario Externo](#flujo-de-usuario-externo)
9. [Validaciones](#validaciones)
10. [Códigos de Error](#códigos-de-error)
11. [Seguridad](#seguridad)
12. [Ejemplos](#ejemplos)
13. [Implementación Detallada](#implementación-detallada)
14. [Testing](#testing)
15. [Historial de Cambios](#historial-de-cambios)

---

## Descripción General

### Propósito

Autenticar usuarios en el sistema mediante email y contraseña, detectando automáticamente si es un usuario interno (vinculado a una compañía) o externo (sin compañía), y ejecutando el flujo correspondiente.

### Alcance

**En alcance:**
- ✅ Validación de credenciales (email y contraseña)
- ✅ Detección automática del tipo de usuario
- ✅ Flujo completo para usuarios internos (ADMIN, COLLA)
- ✅ Flujo simplificado para usuarios externos (USER)
- ✅ Generación de tokens JWT según tipo de usuario
- ✅ Obtención de menús según permisos del rol

**Fuera de alcance:**
- ❌ Registro de usuarios (ver flujos 07-01 y 07-02)
- ❌ Recuperación de contraseña
- ❌ Autenticación de dos factores (2FA)

### Características

| Característica | Usuario Interno | Usuario Externo |
|----------------|-----------------|-----------------|
| Compañía | ✅ Requerida | ❌ No aplica |
| Ubicación | ✅ Requerida | ❌ No aplica |
| Rol | ADMIN, COLLA | USER |
| Menú | Por compañía + permisos | Global + permisos USER |
| Multi-compañía | ✅ Soportado | ❌ No aplica |
| Multi-ubicación | ✅ Soportado | ❌ No aplica |

---

## Arquitectura del Orquestador

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              auth_router.py                                  │
│                         POST /api/v1/auth/login                             │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            auth_controller.py                                │
│                         login(config, params)                                │
│                                  │                                           │
│    Solo llama al orquestador ────┘                                           │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   AuthLoginOrchestratorUseCase                               │
│                                                                              │
│  1. Validar credenciales (AuthValidateUserUseCase)                          │
│  2. Detectar tipo de usuario por ROL (CheckUserTypeByRolUseCase)            │
│  3. Redirigir al flujo correspondiente:                                     │
│                                                                              │
│     ┌─────────────────────┐         ┌─────────────────────┐                 │
│     │   is_internal?      │         │                     │                 │
│     │                     │         │                     │                 │
│     │  ┌────────┐  ┌────────────┐   │                     │                 │
│     │  │  SÍ    │  │    NO      │   │                     │                 │
│     │  └───┬────┘  └─────┬──────┘   │                     │                 │
│     │      │             │          │                     │                 │
│     │      ▼             ▼          │                     │                 │
│     │ AuthLoginUseCase   AuthLoginExternalUseCase         │                 │
│     │ (Internos)         (Externos)                       │                 │
│     └─────────────────────┴─────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Principios de Diseño

| Principio | Implementación |
|-----------|----------------|
| **Single Responsibility** | Cada use case tiene una única responsabilidad |
| **Open/Closed** | Fácil agregar nuevos tipos de usuario |
| **Controller delgado** | Controller solo llama al orquestador |
| **Lógica en dominio** | Toda la lógica de negocio en use cases |

---

## Endpoint

### Especificación

```
POST /api/v1/auth/login
```

### Headers Requeridos

| Header | Valor | Descripción |
|--------|-------|-------------|
| `Content-Type` | `application/json` | Tipo de contenido |
| `Language` | `es` \| `en` | Idioma para mensajes (opcional) |

### Request Body

```json
{
  "email": "usuario@example.com",
  "password": "SecurePassword123!"
}
```

### Response - Usuario Interno (ADMIN/COLLA)

**Éxito (200 OK):**
```json
{
  "data": {
    "platform_configuration": {
      "user": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "admin@goluti.com",
        "first_name": "Admin",
        "last_name": "User",
        "phone": "+573001234567",
        "state": true
      },
      "currency": {
        "id": "660e8400-e29b-41d4-a716-446655440000",
        "name": "Peso Colombiano",
        "code": "COP",
        "symbol": "$",
        "state": true
      },
      "location": {
        "id": "770e8400-e29b-41d4-a716-446655440000",
        "name": "Sede Principal",
        "address": "Calle 123 #45-67",
        "city_id": "dd0e8400-e29b-41d4-a716-446655440000",
        "phone": "+573001234567",
        "email": "sede@goluti.com",
        "main_location": true,
        "latitude": 4.7110,
        "longitude": -74.0721,
        "google_place_id": "ChIJKcjGRmCZP44RFDl2eLPvBBo",
        "state": true
      },
      "language": {
        "id": "880e8400-e29b-41d4-a716-446655440000",
        "name": "Español",
        "code": "es",
        "native_name": "Español",
        "state": true
      },
      "platform": {
        "id": "990e8400-e29b-41d4-a716-446655440000",
        "language_id": "880e8400-e29b-41d4-a716-446655440000",
        "location_id": "770e8400-e29b-41d4-a716-446655440000",
        "token_expiration_minutes": 60,
        "currency_id": "660e8400-e29b-41d4-a716-446655440000"
      },
      "country": {
        "id": "aa0e8400-e29b-41d4-a716-446655440000",
        "name": "Colombia",
        "code": "CO",
        "phone_code": "+57",
        "state": true
      },
      "company": {
        "id": "bb0e8400-e29b-41d4-a716-446655440000",
        "name": "Mi Empresa",
        "inactivity_time": 30,
        "nit": "900123456-7",
        "state": true
      },
      "rol": {
        "id": "cc0e8400-e29b-41d4-a716-446655440000",
        "name": "Administrador",
        "code": "ADMIN",
        "description": "Rol de administrador del sistema",
        "state": true
      },
      "permissions": [
        {"id": "...", "name": "READ", "description": "Lectura", "state": true},
        {"id": "...", "name": "SAVE", "description": "Creación", "state": true},
        {"id": "...", "name": "UPDATE", "description": "Actualización", "state": true},
        {"id": "...", "name": "DELETE", "description": "Eliminación", "state": true},
        {"id": "...", "name": "APPOINTMENTS", "description": "Gestión de Citas", "state": true}
      ],
      "menu": [
        {
          "id": "ff0e8400-e29b-41d4-a716-446655440000",
          "name": "Gestión de Citas",
          "label": "menu.appointments_management",
          "description": "menu.appointments_management_description",
          "top_id": "ff0e8400-e29b-41d4-a716-446655440000",
          "route": "/appointments-management",
          "state": true,
          "icon": "clock"
        }
      ]
    },
    "platform_variations": {
      "currencies": [...],
      "locations": [...],
      "languages": [...],
      "companies": [...]
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "message": "Información guardada correctamente",
  "notification_type": "success",
  "message_type": "temporary"
}
```

### Response - Usuario Externo (USER)

**Éxito (200 OK):**
```json
{
  "data": {
    "platform_configuration": {
      "user": {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "email": "cliente@gmail.com",
        "first_name": "Cliente",
        "last_name": "Externo",
        "phone": "+573009876543",
        "state": true
      },
      "currency": {
        "id": "660e8400-e29b-41d4-a716-446655440000",
        "name": "Peso Colombiano",
        "code": "COP",
        "symbol": "$",
        "state": true
      },
      "location": null,
      "language": {
        "id": "880e8400-e29b-41d4-a716-446655440000",
        "name": "Español",
        "code": "es",
        "native_name": "Español",
        "state": true
      },
      "platform": {
        "id": "990e8400-e29b-41d4-a716-446655440001",
        "language_id": "880e8400-e29b-41d4-a716-446655440000",
        "location_id": null,
        "token_expiration_minutes": 60,
        "currency_id": "660e8400-e29b-41d4-a716-446655440000"
      },
      "country": {
        "id": "aa0e8400-e29b-41d4-a716-446655440000",
        "name": "Colombia",
        "code": "CO",
        "phone_code": "+57",
        "state": true
      },
      "company": null,
      "rol": {
        "id": "1214ffde-997c-4482-b7fe-2524c828a188",
        "name": "Usuario",
        "code": "USER",
        "description": "Rol de usuario externo",
        "state": true
      },
      "permissions": [
        {"id": "...", "name": "READ", "description": "Lectura", "state": true},
        {"id": "...", "name": "MY_APPOINTMENTS", "description": "Mis Citas", "state": true}
      ],
      "menu": [
        {
          "id": "a0b65172-26d5-4a5c-9c93-6fdfa9a0d46a",
          "name": "Mis Citas",
          "label": "menu.my_appointments",
          "description": "menu.my_appointments_description",
          "top_id": "a0b65172-26d5-4a5c-9c93-6fdfa9a0d46a",
          "route": "/my-appointments",
          "state": true,
          "icon": "calendar"
        }
      ]
    },
    "platform_variations": {
      "currencies": [
        {"id": "...", "name": "Peso Colombiano", "code": "COP", "symbol": "$"},
        {"id": "...", "name": "Dólar Estadounidense", "code": "USD", "symbol": "$"},
        {"id": "...", "name": "Euro", "code": "EUR", "symbol": "€"}
      ],
      "locations": [],
      "languages": [...],
      "companies": []
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "message": "Información guardada correctamente",
  "notification_type": "success",
  "message_type": "temporary"
}
```

**Error (200 con notification_type: error):**
```json
{
  "data": null,
  "message": "Credenciales inválidas",
  "notification_type": "error",
  "message_type": "temporary"
}
```

---

## Diagrama de Flujo

### Flujo Principal (Orquestador)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INICIO: Login Orquestador                                 │
│                    POST /api/v1/auth/login                                   │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  1. VALIDAR CREDENCIALES                                     │
│                  AuthValidateUserUseCase                                     │
│                                                                              │
│   - Buscar usuario por email                                                 │
│   - Verificar contraseña con hash bcrypt                                     │
│   - Verificar usuario activo (state = true)                                  │
│                                                                              │
│   ├── Error: Email no encontrado → "Credenciales inválidas"                 │
│   ├── Error: Contraseña incorrecta → "Credenciales inválidas"               │
│   ├── Error: Usuario inactivo → "Credenciales inválidas"                    │
│   └── Éxito: Retorna UserEntity                                              │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  2. DETECTAR TIPO DE USUARIO                                 │
│                  CheckUserTypeByRolUseCase                                   │
│                                                                              │
│   - Buscar en tabla user_location_rol por user_id                           │
│   - Obtener el rol asociado (JOIN con tabla rol)                            │
│   - Verificar rol.code:                                                      │
│     - Si code IN ('ADMIN', 'COLLA') → Usuario INTERNO                       │
│     - Si code == 'USER'             → Usuario EXTERNO                       │
│                                                                              │
│   Retorna: { is_internal: bool, rol_id: UUID, rol_code: str }               │
│                                                                              │
│   IMPORTANTE: El ROL es la marca irrefutable del tipo de usuario            │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
         ┌──────────────────┐        ┌──────────────────┐
         │   is_internal    │        │   is_external    │
         │      = true      │        │      = false     │
         └────────┬─────────┘        └────────┬─────────┘
                  │                           │
                  ▼                           ▼
┌─────────────────────────────┐  ┌─────────────────────────────┐
│  3A. FLUJO USUARIO INTERNO  │  │  3B. FLUJO USUARIO EXTERNO  │
│  AuthLoginUseCase           │  │  AuthLoginExternalUseCase   │
│                             │  │                             │
│  Ver sección:               │  │  Ver sección:               │
│  "Flujo de Usuario Interno" │  │  "Flujo de Usuario Externo" │
└─────────────────────────────┘  └─────────────────────────────┘
                  │                           │
                  └─────────────┬─────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  4. RETORNAR RESPUESTA                                       │
│                                                                              │
│   AuthLoginResponse {                                                        │
│     platform_configuration: {...}                                            │
│     platform_variations: {...}                                               │
│     token: "JWT..."                                                          │
│   }                                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Modelos de Datos

### Request Model

```python
class AuthLoginRequest(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., max_length=255)
```

### Response Models

#### AuthLoginResponse

```python
class AuthLoginResponse(BaseModel):
    platform_configuration: PlatformConfiguration = Field(...)
    platform_variations: PlatformVariations = Field(...)
    token: str = Field(...)
```

#### PlatformConfiguration

```python
class PlatformConfiguration(BaseModel):
    user: UserLoginResponse = Field(...)
    currency: CurrencyLoginResponse = Field(...)
    location: Optional[LocationLoginResponse] = Field(None)  # None para externos
    language: LanguageLoginResponse = Field(...)
    platform: PlatformLoginResponse = Field(...)
    country: Optional[CountryLoginResponse] = Field(None)    # None para externos
    company: Optional[CompanyLoginResponse] = Field(None)    # None para externos
    rol: RolLoginResponse = Field(...)
    permissions: List[PermissionLoginResponse] = Field(...)
    menu: List[MenuLoginResponse] = Field(...)
```

#### PlatformVariations

```python
class PlatformVariations(BaseModel):
    currencies: List[CurrencyLoginResponse] = Field(default=[])  # [] para externos
    locations: List[LocationLoginResponse] = Field(default=[])   # [] para externos
    languages: List[LanguageLoginResponse] = Field(...)
    companies: List[CompanyLoginResponse] = Field(default=[])    # [] para externos
```

#### PlatformLoginResponse (Actualizado)

```python
class PlatformLoginResponse(BaseModel):
    id: UUID4 = Field(...)
    language_id: UUID4 = Field(...)
    location_id: Optional[UUID4] = Field(None)  # None para externos
    token_expiration_minutes: int = Field(...)
    currency_id: UUID4 = Field(...)
```

---

## Campo `type` en Tabla Menu

### Justificación

Para garantizar la seguridad y correcta separación de menús entre usuarios internos y externos, se agrega un campo `type` a la tabla `menu`. Esto evita:

1. **Ambigüedad**: `company_id IS NULL` podría significar "menú global de sistema" (interno) o "menú para externos"
2. **Riesgos de seguridad**: Sin este campo, un usuario externo podría ver menús internos si se comete un error en el query
3. **Filtrado explícito**: El campo `type` permite validación directa y clara

### Valores del Campo

| Valor | Descripción | Visible para |
|-------|-------------|--------------|
| `INTERNAL` | Menús para usuarios internos | ADMIN, COLLA |
| `EXTERNAL` | Menús para usuarios externos | USER |
| `BOTH` | Menús para ambos tipos (futuro) | Todos |

### Enum en Python

**Archivo:** `src/core/enums/menu_type.py`

```python
from enum import Enum

class MENU_TYPE(Enum):
    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"
    BOTH = "BOTH"
```

### Actualización de MenuEntity

**Archivo:** `src/infrastructure/database/entities/menu_entity.py`

```python
class MenuEntity(Base):
    __tablename__ = "menu"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company.id"), nullable=True)
    name = Column(String(100), nullable=False)
    label = Column(String(300), nullable=False)
    description = Column(String(300), nullable=True)
    top_id = Column(UUID(as_uuid=True), nullable=False)
    route = Column(String(300), nullable=False)
    state = Column(Boolean, default=True)
    icon = Column(String(50), nullable=True)
    type = Column(String(20), nullable=False, default="INTERNAL")  # NUEVO
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### Migración de Base de Datos

**Archivo:** `migrations/changelog-v47.sql`

```sql
-- liquibase formatted sql
-- changeset add-menu-type-column:1736704200000-47

-- ============================================
-- 1. Agregar columna type a tabla menu
-- ============================================

ALTER TABLE menu ADD COLUMN type VARCHAR(20) NOT NULL DEFAULT 'INTERNAL';

-- ============================================
-- 2. Actualizar menús existentes
-- Todos los menús actuales son INTERNAL por defecto
-- ============================================

-- Los menús con company_id = NULL que son para externos se actualizan
UPDATE menu 
SET type = 'EXTERNAL'
WHERE id = 'a0b65172-26d5-4a5c-9c93-6fdfa9a0d46a';  -- Mis Citas

-- ============================================
-- 3. Crear índice para optimizar consultas
-- ============================================

CREATE INDEX idx_menu_type ON menu(type);

--ROLLBACK DROP INDEX IF EXISTS idx_menu_type;
--ROLLBACK ALTER TABLE menu DROP COLUMN type;
```

### Queries Actualizados

#### Para Usuarios Internos

```python
# auth_repository.py - método menu()

async def menu(self, config: Config, params: Menu):
    async with config.async_db as db:
        stmt = (
            select(MenuPermissionEntity, MenuEntity)
            .join(MenuPermissionEntity, MenuPermissionEntity.menu_id == MenuEntity.id)
            .filter(MenuEntity.company_id == params.company)
            .filter(MenuEntity.type == "INTERNAL")  # ← Seguridad adicional
            .filter(MenuEntity.state == True)
        )
        result = await db.execute(stmt)
        return result.all()
```

#### Para Usuarios Externos

```python
# auth_repository.py - método menu_external()

async def menu_external(self, config: Config, permission_ids: List[str]):
    async with config.async_db as db:
        stmt = (
            select(MenuPermissionEntity, MenuEntity)
            .join(MenuPermissionEntity, MenuPermissionEntity.menu_id == MenuEntity.id)
            .filter(MenuEntity.type == "EXTERNAL")  # ← Filtro por tipo
            .filter(MenuPermissionEntity.permission_id.in_(permission_ids))
            .filter(MenuEntity.state == True)
        )
        result = await db.execute(stmt)
        return result.all()
```

### Impacto en Otros Servicios

El campo `type` también afecta otros servicios que trabajan con menús:

#### Create Company (Clonación de Menús)

**Archivo:** `src/domain/services/use_cases/business/auth/create_company/create_company_use_case.py`

Cuando se crea una compañía, se clonan los menús template (con `company_id = NULL`). Ahora también debe filtrarse por `type = 'INTERNAL'`:

```python
# ANTES (líneas 205-225):
template_menus = await self.menu_list_uc.execute(
    config=config,
    params=Pagination(
        filters=[
            FilterManager(
                field="company_id",
                value=None,
                condition=CONDITION_TYPE.EQUALS
            )
        ],
        all_data=True
    )
)

# DESPUÉS:
template_menus = await self.menu_list_uc.execute(
    config=config,
    params=Pagination(
        filters=[
            FilterManager(
                field="company_id",
                value=None,
                condition=CONDITION_TYPE.EQUALS
            ),
            FilterManager(
                field="type",
                value="INTERNAL",  # ← Solo clonar menús internos
                condition=CONDITION_TYPE.EQUALS
            )
        ],
        all_data=True
    )
)
```

**Razón:** Los menús `EXTERNAL` (como "Mis Citas") son globales y no deben clonarse por compañía. Solo los menús `INTERNAL` se clonan para cada nueva compañía.

---

## Centralización de Roles en user_location_rol

Para unificar la gestión de roles y simplificar la detección del tipo de usuario, **todos los usuarios** (internos y externos) deben tener un registro en la tabla `user_location_rol`.

### Cambios en user_location_rol

**Cambio principal:** El campo `location_id` ahora es **nullable** para permitir usuarios externos sin ubicación asociada.

#### Migración

**Archivo:** `migrations/changelog-v48.sql`

```sql
-- liquibase formatted sql
-- changeset user-location-rol-nullable-location:1736790600000-48

-- ============================================
-- 1. Hacer location_id nullable
-- ============================================

ALTER TABLE user_location_rol ALTER COLUMN location_id DROP NOT NULL;

-- ============================================
-- 2. Crear índice para usuarios externos (location_id IS NULL)
-- ============================================

CREATE INDEX idx_user_location_rol_external 
ON user_location_rol(user_id, rol_id) 
WHERE location_id IS NULL;

-- ============================================
-- 3. Comentario para documentación
-- ============================================

COMMENT ON COLUMN user_location_rol.location_id IS 
'ID de la ubicación. NULL para usuarios externos (rol USER).';

--ROLLBACK DROP INDEX IF EXISTS idx_user_location_rol_external;
--ROLLBACK ALTER TABLE user_location_rol ALTER COLUMN location_id SET NOT NULL;
```

### Tabla user_country (NUEVA)

Para asociar países a usuarios externos y poder retornar el `country` en la respuesta de login.

**Archivo:** `migrations/changelog-v49.sql`

```sql
-- liquibase formatted sql
-- changeset create-user-country-table:1736877000000-49

-- ============================================
-- 1. Crear tabla user_country
-- ============================================

CREATE TABLE user_country (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE,
    country_id UUID NOT NULL,
    state BOOLEAN NOT NULL DEFAULT TRUE,
    created_date TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_date TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT fk_user_country_user 
        FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    CONSTRAINT fk_user_country_country 
        FOREIGN KEY (country_id) REFERENCES geo_division(id) ON DELETE RESTRICT
);

-- ============================================
-- 2. Crear índices
-- ============================================

CREATE INDEX idx_user_country_user_id ON user_country(user_id);
CREATE INDEX idx_user_country_country_id ON user_country(country_id);

-- ============================================
-- 3. Comentarios
-- ============================================

COMMENT ON TABLE user_country IS 'Asocia usuarios externos con su país de origen';
COMMENT ON COLUMN user_country.user_id IS 'ID del usuario (único - un usuario solo tiene un país)';
COMMENT ON COLUMN user_country.country_id IS 'ID del país asociado (geo_division tipo COUNTRY)';

--ROLLBACK DROP TABLE IF EXISTS user_country;
```

**Entity:**

```python
# src/infrastructure/database/entities/user_country_entity.py

from sqlalchemy import Column, ForeignKey, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from src.infrastructure.database.config.base import Base


class UserCountryEntity(Base):
    __tablename__ = "user_country"

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, unique=True)
    country_id = Column(UUID(as_uuid=True), nullable=False)  # FK a geo_division(id) - nodo tipo COUNTRY
    state = Column(Boolean, nullable=False, default=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("UserEntity", back_populates="user_country")
    country = relationship("GeoDivisionEntity", foreign_keys=[country_id])
```

**Impacto en CreateUserExternalUseCase:**

```python
# Agregar country_id al request
class CreateUserExternalRequest(BaseModel):
    # ... campos existentes ...
    country_id: UUID  # NUEVO - País del usuario

# En el use case, después de crear el usuario:
user_country = UserCountryEntity(
    id=uuid4(),
    user_id=user_created.id,
    country_id=params.country_id,
    state=True,
    created_date=datetime.utcnow(),
    updated_date=datetime.utcnow()
)
config.session.add(user_country)
```

### Estructura de user_location_rol

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        user_location_rol                                     │
├──────────────────┬──────────────────┬──────────────────┬────────────────────┤
│     user_id      │   location_id    │     rol_id       │      Tipo          │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ uuid-user-1      │ uuid-location-1  │ uuid-rol-ADMIN   │ INTERNO (Admin)    │
│ uuid-user-2      │ uuid-location-2  │ uuid-rol-COLLA   │ INTERNO (Colla)    │
│ uuid-user-3      │ NULL             │ uuid-rol-USER    │ EXTERNO (Usuario)  │
└──────────────────┴──────────────────┴──────────────────┴────────────────────┘

NOTA: El rol.code es la marca irrefutable del tipo de usuario:
      - ADMIN, COLLA → Usuario INTERNO (tiene company, location)
      - USER → Usuario EXTERNO (no tiene company ni location)
```

### Modificación de CreateUserExternalUseCase

**Archivo:** `src/domain/services/use_cases/business/auth/create_user_external/create_user_external_use_case.py`

Actualmente, este use case crea el usuario en la tabla `user` pero **no lo registra en `user_location_rol`**. Esto debe modificarse:

```python
# AGREGAR al final del método execute(), después de crear el usuario:

# Registrar en user_location_rol con el rol USER
user_location_rol = UserLocationRolEntity(
    id=uuid4(),
    user_id=user.id,
    location_id=None,  # ← NULL para usuarios externos
    rol_id=UUID("1214ffde-997c-4482-b7fe-2524c828a188"),  # Rol USER
    state=True,
    created_date=datetime.utcnow(),
    updated_date=datetime.utcnow()
)
config.session.add(user_location_rol)
```

**Razón:** Con este registro, el `CheckUserTypeByRolUseCase` puede detectar el tipo de usuario consultando únicamente la tabla `user_location_rol` y verificando el código del rol.

### Ventajas de esta Arquitectura

| Aspecto | Beneficio |
|---------|-----------|
| **Centralización** | Todos los roles en una sola tabla |
| **Detección simple** | Una sola consulta para determinar tipo de usuario |
| **Extensibilidad** | Fácil agregar nuevos roles externos en el futuro |
| **Consistencia** | El rol es la fuente de verdad para el tipo de usuario |
| **Performance** | Índice parcial optimiza queries de usuarios externos |

---

## Casos de Uso Afectados por los Cambios

Esta sección documenta **todos** los casos de uso que requieren modificación para soportar usuarios externos.

### Resumen de Impacto

| Use Case | Archivo | Tipo de Cambio | Prioridad |
|----------|---------|----------------|-----------|
| `AuthLoginUseCase` | `auth_login_use_case.py` | Reemplazar por orquestador en controller | 🔴 Alta |
| `AuthRefreshTokenUseCase` | `auth_refresh_token_use_case.py` | **⚠️ CRÍTICO** - Crear orquestador | 🔴 Alta |
| `CreateUserExternalUseCase` | `create_user_external_use_case.py` | Agregar registro en `user_location_rol` | 🔴 Alta |
| `DeleteUserExternalUseCase` | `delete_user_external_use_case.py` | Eliminar registro de `user_location_rol` | 🟡 Media |
| `CreateCompanyUseCase` | `create_company_use_case.py` | Filtrar por `type = 'INTERNAL'` | 🟡 Media |
| `AuthMenuUseCase` | `auth_menu_use_case.py` | Agregar filtro `type = 'INTERNAL'` | 🟡 Media |

---

### 1. AuthRefreshTokenUseCase (CRÍTICO)

**Archivo:** `src/domain/services/use_cases/business/auth/refresh_token/auth_refresh_token_use_case.py`

**Problema:** El caso de uso actual asume que **todos los usuarios son internos**:

```python
# Línea 93-107 - Obtiene datos que serán NULL para externos
initial_user_data = self.auth_initial_user_data_use_case.execute(...)
# Retorna: platform, user, language, location, currency, country, company
#          ↑ location y company serán NULL para usuarios externos

# Línea 109-116 - Requiere location_entity.id (NULL para externos)
user_role_and_permissions = self.auth_user_role_and_permissions_use_case.execute(
    params=AuthUserRoleAndPermissions(
        email=user_read.email, 
        location=location_entity.id  # ❌ ERROR: NULL para externos
    ),
)

# Línea 122-125 - Requiere company_entity.id (NULL para externos)
auth_menu = self.auth_menu_use_case.execute(
    params=AuthMenu(
        company=company_entity.id,  # ❌ ERROR: NULL para externos
        permissions=permissions
    ),
)
```

**Solución:** Crear `AuthRefreshTokenOrchestratorUseCase` con la misma lógica del login:

```python
# auth_refresh_token_orchestrator_use_case.py (NUEVO)

from src.domain.services.use_cases.business.auth.login.check_user_type_by_rol_use_case import (
    CheckUserTypeByRolUseCase,
)

class AuthRefreshTokenOrchestratorUseCase:
    def __init__(self):
        self.check_user_type_by_rol_use_case = CheckUserTypeByRolUseCase()
        self.auth_refresh_token_use_case = AuthRefreshTokenUseCase()  # Internos
        self.auth_refresh_token_external_use_case = AuthRefreshTokenExternalUseCase()  # Externos

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(self, config: Config) -> Union[AuthRefreshTokenResponse, str, None]:
        
        # 1. Detectar tipo de usuario por ROL
        user_type_info = await self.check_user_type_by_rol_use_case.execute(
            config=config, user_id=config.token.user_id
        )
        
        if user_type_info is None:
            return "Usuario sin rol asignado"

        # 2. Redirigir al flujo correspondiente
        if user_type_info.is_internal:
            return await self.auth_refresh_token_use_case.execute(config=config)
        else:
            return await self.auth_refresh_token_external_use_case.execute(
                config=config,
                rol_id=user_type_info.rol_id
            )
```

**AuthRefreshTokenExternalUseCase (NUEVO):**

```python
# auth_refresh_token_external_use_case.py

class AuthRefreshTokenExternalUseCase:
    def __init__(self):
        self.user_read_use_case = UserReadUseCase(user_repository)
        self.user_update_use_case = UserUpdateUseCase(user_repository)
        self.auth_languages_use_case = AuthLanguagesUseCase()
        self.auth_external_rol_and_permissions_use_case = AuthExternalRolAndPermissionsUseCase()
        self.auth_menu_external_use_case = AuthMenuExternalUseCase()
        self.token = Token()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self, 
        config: Config,
        rol_id: UUID
    ) -> Union[AuthRefreshTokenResponse, str, None]:
        
        # 1. Obtener usuario
        user = await self.user_read_use_case.execute(
            config=config, params=UserRead(id=config.token.user_id)
        )
        if isinstance(user, str):
            return user

        # 2. Obtener platform del usuario
        platform = await self._get_platform(config, user.platform_id)

        # 3. Obtener rol y permisos (usando rol_id ya conocido)
        rol, permissions = await self.auth_external_rol_and_permissions_use_case.execute(
            config=config, rol_id=rol_id
        )

        # 4. Obtener menú externo
        menu = await self.auth_menu_external_use_case.execute(
            config=config, permissions=permissions
        )

        # 5. Obtener idiomas
        languages = await self.auth_languages_use_case.execute(config=config)

        # 6. Generar token (sin company ni location)
        access_token = AccessToken(
            rol_id=str(rol.id),
            rol_code=str(rol.code),
            user_id=str(user.id),
            location_id=None,      # ← NULL para externos
            currency_id=str(platform.currency_id),
            company_id=None,       # ← NULL para externos
            token_expiration_minutes=platform.token_expiration_minutes,
            permissions=[p.name for p in permissions],
        )

        token = self.token.refresh_access_token(
            refresh_token=user.refresh_token, 
            data=access_token
        )
        refresh_token = self.token.create_refresh_token(data=access_token)

        # 7. Actualizar refresh_token del usuario
        await self.user_update_use_case.execute(
            config=config,
            params=UserUpdate(
                id=user.id,
                refresh_token=refresh_token,
                # ... otros campos
            ),
        )

        return AuthRefreshTokenResponse(token=token)
```

---

### 2. DeleteUserExternalUseCase

**Archivo:** `src/domain/services/use_cases/business/auth/delete_user_external/delete_user_external_use_case.py`

**Cambio requerido:** Al hacer **hard delete**, también eliminar el registro de `user_location_rol`.

```python
# En _execute_hard_delete(), AGREGAR antes de eliminar user:

async def _execute_hard_delete(
    self,
    config: Config,
    params: DeleteUserExternalRequest,
    platform_id: UUID4
) -> None:
    """Ejecuta la eliminación física del usuario y sus registros relacionados."""
    
    # NUEVO: Eliminar registro de user_location_rol
    await self.user_location_rol_repository.delete_by_user_id(
        config=config, 
        user_id=params.user_id
    )
    
    # Eliminar user
    user_deleted = await self.user_delete_uc.execute(
        config=config,
        params=UserDelete(id=params.user_id)
    )
    if isinstance(user_deleted, str):
        raise Exception("Error deleting user")

    # Eliminar platform
    platform_deleted = await self.platform_delete_uc.execute(
        config=config,
        params=PlatformDelete(id=platform_id)
    )
    if isinstance(platform_deleted, str):
        raise Exception("Error deleting platform")
```

**Query del repositorio:**

```python
# En user_location_rol_repository.py o auth_repository.py

async def delete_by_user_id(self, config: Config, user_id: UUID) -> None:
    """Elimina todos los registros de user_location_rol para un usuario."""
    query = (
        config.session.query(UserLocationRolEntity)
        .filter(UserLocationRolEntity.user_id == user_id)
    )
    await sync_to_async(query.delete)()
```

---

### 3. AuthController

**Archivo:** `src/infrastructure/web/controller/business/auth_controller.py`

**Cambios requeridos:**

```python
# ANTES (línea 94):
self.auth_login_use_case = AuthLoginUseCase()

# DESPUÉS:
self.auth_login_orchestrator_use_case = AuthLoginOrchestratorUseCase()

# ANTES (línea 95):
self.auth_refresh_token_use_case = AuthRefreshTokenUseCase()

# DESPUÉS:
self.auth_refresh_token_orchestrator_use_case = AuthRefreshTokenOrchestratorUseCase()
```

```python
# Método login (línea 109-121):
async def login(self, config: Config, params: AuthLoginRequest) -> Response:
    result = await self.auth_login_orchestrator_use_case.execute(  # ← Cambiar
        config=config, params=params
    )
    # ... resto igual

# Método refresh_token (línea 123-136):
async def refresh_token(self, config: Config) -> Response:
    result = await self.auth_refresh_token_orchestrator_use_case.execute(  # ← Cambiar
        config=config
    )
    # ... resto igual
```

---

### 4. Resumen de Archivos a Crear/Modificar

#### Archivos NUEVOS:

| Archivo | Descripción |
|---------|-------------|
| `check_user_type_by_rol_use_case.py` | Detecta tipo de usuario por rol |
| `auth_login_orchestrator_use_case.py` | Orquesta login interno/externo |
| `auth_login_external_use_case.py` | Login para usuarios externos |
| `auth_initial_external_user_data_use_case.py` | Datos iniciales externos |
| `auth_external_rol_and_permissions_use_case.py` | Rol y permisos externos |
| `auth_menu_external_use_case.py` | Menú para externos |
| `auth_refresh_token_orchestrator_use_case.py` | Orquesta refresh token |
| `auth_refresh_token_external_use_case.py` | Refresh token externos |

#### Archivos a MODIFICAR:

| Archivo | Cambio |
|---------|--------|
| `auth_controller.py` | Usar orquestadores |
| `auth_menu_use_case.py` | Agregar filtro `type = 'INTERNAL'` |
| `create_user_external_use_case.py` | Agregar registro en `user_location_rol` |
| `delete_user_external_use_case.py` | Eliminar registro de `user_location_rol` |
| `create_company_use_case.py` | Filtrar menús por `type = 'INTERNAL'` |
| `auth_repository.py` | Nuevos métodos para queries externos |

#### Migraciones:

| Archivo | Cambio |
|---------|--------|
| `changelog-v47.sql` | Agregar columna `type` a tabla `menu` |
| `changelog-v48.sql` | Hacer `location_id` nullable en `user_location_rol` |
| `changelog-v49.sql` | Crear tabla `user_country` para asociar país a usuarios externos |

---

### Flujo de Asignación de Menú Externo

Para que un menú sea visible para usuarios externos, debe cumplir:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    REQUISITOS PARA MENÚ EXTERNO                              │
└─────────────────────────────────────────────────────────────────────────────┘

1. TABLA MENU
   ├── type = 'EXTERNAL'
   ├── state = true
   └── (company_id puede ser NULL o no, se filtra por type)

2. TABLA PERMISSION
   └── Debe existir el permiso (ej: MY_APPOINTMENTS)

3. TABLA MENU_PERMISSION
   └── Vincular menu_id con permission_id

4. TABLA ROL_PERMISSION
   └── Vincular permission_id con rol USER (1214ffde-997c-4482-b7fe-2524c828a188)

Resultado: Usuario con rol USER verá el menú al hacer login
```

---

## Casos de Uso

### Estructura de Archivos

```
src/domain/services/use_cases/business/auth/login/
├── auth_login_orchestrator_use_case.py      # NUEVO - Orquestador principal
├── auth_login_use_case.py                   # Existente - Usuarios internos
├── auth_login_external_use_case.py          # NUEVO - Usuarios externos
├── check_user_location_rol_use_case.py      # NUEVO - Detecta tipo de usuario
├── auth_validate_user_use_case.py           # Existente - Valida credenciales
├── auth_initial_user_data_use_case.py       # Existente - Datos usuarios internos
├── auth_initial_external_user_data_use_case.py  # NUEVO - Datos usuarios externos
├── auth_external_rol_and_permissions_use_case.py # NUEVO - Rol y permisos externos
├── auth_menu_external_use_case.py           # NUEVO - Menú usuarios externos
├── auth_user_role_and_permissions.py        # Existente - Rol usuarios internos
├── auth_menu_use_case.py                    # Existente - Menú usuarios internos
├── companies_by_user_use_case.py            # Existente - Compañías del usuario
├── auth_currencies_use_case.py              # Existente
├── auth_locations_use_case.py               # Existente
├── auth_languages_use_case.py               # Existente
└── __init__.py
```

### Casos de Uso por Tipo de Usuario

| Use Case | Interno | Externo | Descripción |
|----------|---------|---------|-------------|
| `AuthLoginOrchestratorUseCase` | ✅ | ✅ | Orquesta todo el flujo |
| `AuthValidateUserUseCase` | ✅ | ✅ | Valida credenciales |
| `CheckUserTypeByRolUseCase` | ✅ | ✅ | Detecta tipo de usuario por rol (ADMIN/COLLA = interno, USER = externo) |
| `AuthLoginUseCase` | ✅ | ❌ | Flujo completo interno |
| `AuthLoginExternalUseCase` | ❌ | ✅ | Flujo simplificado externo |
| `CompaniesByUserUseCase` | ✅ | ❌ | Obtiene compañías |
| `AuthInitialUserDataUseCase` | ✅ | ❌ | Datos iniciales internos |
| `AuthInitialExternalUserDataUseCase` | ❌ | ✅ | Datos iniciales externos |
| `AuthUserRoleAndPermissionsUseCase` | ✅ | ❌ | Rol y permisos internos |
| `AuthExternalRolAndPermissionsUseCase` | ❌ | ✅ | Rol y permisos externos |
| `AuthMenuUseCase` | ✅ | ❌ | Menú por compañía (type = INTERNAL) |
| `AuthMenuExternalUseCase` | ❌ | ✅ | Menú externo (type = EXTERNAL) |
| `AuthCurrenciesUseCase` | ✅ | ❌ | Monedas de ubicación |
| `AuthLocationsUseCase` | ✅ | ❌ | Ubicaciones del usuario |
| `AuthLanguagesUseCase` | ✅ | ✅ | Idiomas disponibles |

---

## Flujo de Usuario Interno

```
┌─────────────────────────────────────────────────────────────────────────────┐
│               FLUJO USUARIO INTERNO (AuthLoginUseCase)                       │
│               Roles: ADMIN, COLLA                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. OBTENER COMPAÑÍAS DEL USUARIO                                             │
│    CompaniesByUserUseCase                                                    │
│    - Query: user → user_location_rol → location → company                    │
│    - Retorna: List[Company]                                                  │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. OBTENER DATOS INICIALES                                                   │
│    AuthInitialUserDataUseCase                                                │
│    - Query: user → platform → language, location, currency, geo_division(country), company │
│    - Retorna: Tuple[Platform, User, Language, Location, Currency,            │
│               GeoDivision(Country), Company]                                 │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. OBTENER ROL Y PERMISOS                                                    │
│    AuthUserRoleAndPermissionsUseCase                                         │
│    - Query: user → user_location_rol → rol → rol_permission → permission     │
│    - Filtra por: location_id                                                 │
│    - Retorna: Tuple[List[Permission], Rol]                                   │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. OBTENER MENÚ                                                              │
│    AuthMenuUseCase                                                           │
│    - Query: menu WHERE company_id = ? AND type = 'INTERNAL'                  │
│    - Filtra por: permisos del usuario                                        │
│    - Retorna: List[Menu]                                                     │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 5. OBTENER VARIACIONES                                                       │
│    - AuthCurrenciesUseCase → Monedas de la ubicación                         │
│    - AuthLocationsUseCase → Ubicaciones del usuario en la compañía           │
│    - AuthLanguagesUseCase → Idiomas disponibles                              │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 6. GENERAR TOKEN                                                             │
│    AccessToken {                                                             │
│      rol_id: "...",                                                          │
│      rol_code: "ADMIN" | "COLLA",                                            │
│      user_id: "...",                                                         │
│      location_id: "...",         ← Tiene valor                               │
│      currency_id: "...",                                                     │
│      company_id: "...",          ← Tiene valor                               │
│      permissions: ["READ", "SAVE", "UPDATE", "DELETE", ...]                  │
│    }                                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Entidades Involucradas (Interno)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│     USER     │────▶│   PLATFORM   │────▶│   LANGUAGE   │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    
       │                    ▼                    
       │             ┌──────────────┐     ┌──────────────┐
       │             │   LOCATION   │────▶│   CURRENCY   │
       │             └──────────────┘     └──────────────┘
       │                    │
       │                    ▼
       │             ┌──────────────┐     ┌──────────────┐
       └────────────▶│   COMPANY    │────▶│ GEO_DIVISION │
                     └──────────────┘     │  (COUNTRY)   │
                                          └──────────────┘
                            │
                            ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│USER_LOC_ROL  │────▶│     ROL      │────▶│ ROL_PERMISSION│
└──────────────┘     └──────────────┘     └──────────────┘
                                                │
                                                ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│     MENU     │────▶│MENU_PERMISSION│────▶│  PERMISSION  │
└──────────────┘     └──────────────┘     └──────────────┘
```

---

## Flujo de Usuario Externo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│             FLUJO USUARIO EXTERNO (AuthLoginExternalUseCase)                 │
│             Rol: USER (1214ffde-997c-4482-b7fe-2524c828a188)                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. OBTENER DATOS INICIALES EXTERNOS                                          │
│    AuthInitialExternalUserDataUseCase                                        │
│    - Query: user → platform → language, currency                             │
│    - NO hace JOIN con location, company, country                             │
│    - Retorna: Tuple[Platform, User, Language, Currency]                      │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. OBTENER ROL Y PERMISOS EXTERNOS                                           │
│    AuthExternalRolAndPermissionsUseCase                                      │
│    - Obtiene rol USER (ID fijo: 1214ffde-997c-4482-b7fe-2524c828a188)        │
│    - Query: rol → rol_permission → permission                                │
│    - Retorna: Tuple[List[Permission], Rol]                                   │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. OBTENER MENÚ EXTERNO                                                      │
│    AuthMenuExternalUseCase                                                   │
│    - Query: menu WHERE type = 'EXTERNAL'                                     │
│    - Filtra por: permisos del rol USER (ej: MY_APPOINTMENTS)                 │
│    - Retorna: List[Menu]                                                     │
│                                                                              │
│    Menús esperados:                                                          │
│    - "Mis Citas" (/my-appointments, icon: calendar)                          │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. OBTENER IDIOMAS                                                           │
│    AuthLanguagesUseCase                                                      │
│    - Retorna: List[Language]                                                 │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 5. GENERAR TOKEN                                                             │
│    AccessToken {                                                             │
│      rol_id: "1214ffde-997c-4482-b7fe-2524c828a188",                         │
│      rol_code: "USER",                                                       │
│      user_id: "...",                                                         │
│      location_id: null,          ← Sin ubicación                             │
│      currency_id: "...",                                                     │
│      company_id: null,           ← Sin compañía                              │
│      permissions: ["READ", "MY_APPOINTMENTS"]                                │
│    }                                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Entidades Involucradas (Externo)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│     USER     │────▶│   PLATFORM   │────▶│   LANGUAGE   │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   CURRENCY   │
                     └──────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│     ROL      │────▶│ROL_PERMISSION│────▶│  PERMISSION  │
│    (USER)    │     └──────────────┘     └──────────────┘
└──────────────┘            

┌──────────────┐     ┌──────────────┐
│     MENU     │────▶│MENU_PERMISSION│
│ (type =      │     └──────────────┘
│  'EXTERNAL') │
└──────────────┘
```

### Diferencias Clave

| Aspecto | Usuario Interno | Usuario Externo |
|---------|-----------------|-----------------|
| **Detección** | Tiene registro en `user_location_rol` | NO tiene registro en `user_location_rol` |
| **Platform.location_id** | UUID válido | `NULL` |
| **Rol** | Obtenido de `user_location_rol` | Fijo: USER (1214ffde...) |
| **Menú query** | `WHERE company_id = ? AND type = 'INTERNAL'` | `WHERE type = 'EXTERNAL'` |
| **Token.company_id** | UUID de la compañía | `NULL` o string vacío |
| **Token.location_id** | UUID de la ubicación | `NULL` o string vacío |
| **Variaciones** | Completas | Solo idiomas |

---

## Validaciones

### Reglas de Negocio

1. **Email Existe**: El email debe existir en la tabla `user`
2. **Contraseña Válida**: La contraseña debe coincidir con el hash bcrypt
3. **Usuario Activo**: El usuario debe tener `state = true`
4. **Tipo de Usuario**: Se determina por existencia en `user_location_rol`

### Validaciones por Tipo

| Validación | Interno | Externo | Descripción |
|------------|---------|---------|-------------|
| Email existe | ✅ | ✅ | Busca en tabla `user` |
| Password válido | ✅ | ✅ | Verifica hash bcrypt |
| Usuario activo | ✅ | ✅ | `state = true` |
| Tiene `user_location_rol` | ✅ Requerido | ❌ No debe tener | Determina el tipo |
| Tiene `platform.location_id` | ✅ Requerido | ❌ Debe ser NULL | Consistencia |
| Rol asignado | ✅ Desde BD | ✅ Fijo (USER) | Obtención de permisos |

---

## Códigos de Error

### Escenarios de Error

| Escenario | Mensaje | Tipo Usuario |
|-----------|---------|--------------|
| Email no encontrado | "Credenciales inválidas" | Ambos |
| Contraseña incorrecta | "Credenciales inválidas" | Ambos |
| Usuario inactivo | "Credenciales inválidas" | Ambos |
| Sin configuración platform | "Error de configuración" | Ambos |
| Sin rol USER en BD | "Rol no encontrado" | Externo |
| Sin permisos para rol | "Permisos no encontrados" | Ambos |

**Nota**: Por seguridad, los errores de autenticación retornan un mensaje genérico.

---

## Seguridad

### Consideraciones

1. **Contraseñas Hasheadas**: Hash bcrypt
2. **Tokens JWT**: Firmados con HS256
3. **Refresh Token**: Almacenado en BD para invalidación
4. **Mensajes Genéricos**: No revelar si el email existe
5. **Endpoint Público**: Sin decoradores de permisos (pre-autenticación)

### Estructura del Token JWT

#### Usuario Interno
```python
AccessToken(
    rol_id="b2f212eb-18c2-4260-9223-897685086904",  # ADMIN o COLLA
    rol_code="ADMIN",
    user_id="550e8400-e29b-41d4-a716-446655440000",
    location_id="770e8400-e29b-41d4-a716-446655440000",  # ← Tiene valor
    currency_id="660e8400-e29b-41d4-a716-446655440000",
    company_id="bb0e8400-e29b-41d4-a716-446655440000",   # ← Tiene valor
    permissions=["READ", "SAVE", "UPDATE", "DELETE", "APPOINTMENTS"]
)
```

#### Usuario Externo
```python
AccessToken(
    rol_id="1214ffde-997c-4482-b7fe-2524c828a188",  # USER fijo
    rol_code="USER",
    user_id="550e8400-e29b-41d4-a716-446655440001",
    location_id=None,  # ← NULL
    currency_id="660e8400-e29b-41d4-a716-446655440000",
    company_id=None,   # ← NULL
    permissions=["READ", "MY_APPOINTMENTS"]
)
```

---

## Ejemplos

### Ejemplo 1: Login Usuario Interno (ADMIN)

**Request:**
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@empresa.com",
  "password": "AdminPassword123!"
}
```

**Response:** Ver sección "Response - Usuario Interno"

### Ejemplo 2: Login Usuario Externo (USER)

**Request:**
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "cliente@gmail.com",
  "password": "ClientePassword123!"
}
```

**Response:** Ver sección "Response - Usuario Externo"

### Ejemplo 3: Error - Credenciales Inválidas

**Request:**
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "usuario@example.com",
  "password": "passwordincorrecto"
}
```

**Response:**
```json
{
  "data": null,
  "message": "Credenciales inválidas",
  "notification_type": "error",
  "message_type": "temporary"
}
```

---

## Implementación Detallada

### 1. AuthLoginOrchestratorUseCase (NUEVO)

**Archivo:** `src/domain/services/use_cases/business/auth/login/auth_login_orchestrator_use_case.py`

```python
from typing import Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.login.auth_login_request import AuthLoginRequest
from src.domain.models.business.auth.login.auth_login_response import AuthLoginResponse
from src.domain.services.use_cases.business.auth.login.auth_validate_user_use_case import (
    AuthValidateUserUseCase,
)
from src.domain.services.use_cases.business.auth.login.check_user_type_by_rol_use_case import (
    CheckUserTypeByRolUseCase,
)
from src.domain.services.use_cases.business.auth.login.auth_login_use_case import (
    AuthLoginUseCase,
)
from src.domain.services.use_cases.business.auth.login.auth_login_external_use_case import (
    AuthLoginExternalUseCase,
)


class AuthLoginOrchestratorUseCase:
    def __init__(self):
        self.auth_validate_user_use_case = AuthValidateUserUseCase()
        self.check_user_type_by_rol_use_case = CheckUserTypeByRolUseCase()
        self.auth_login_use_case = AuthLoginUseCase()
        self.auth_login_external_use_case = AuthLoginExternalUseCase()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: AuthLoginRequest,
    ) -> Union[AuthLoginResponse, str, None]:
        
        # 1. Validar credenciales
        user = await self.auth_validate_user_use_case.execute(
            config=config, params=params
        )
        if isinstance(user, str):
            return user

        # 2. Detectar tipo de usuario por ROL (marca irrefutable)
        user_type_info = await self.check_user_type_by_rol_use_case.execute(
            config=config, user_id=user.id
        )

        # 3. Redirigir al flujo correspondiente basado en el rol
        if user_type_info.is_internal:
            return await self.auth_login_use_case.execute(
                config=config, params=params, validated_user=user
            )
        else:
            # Pasar el rol_id para evitar consultas adicionales
            return await self.auth_login_external_use_case.execute(
                config=config, 
                params=params, 
                validated_user=user,
                rol_id=user_type_info.rol_id
            )
```

### 2. CheckUserTypeByRolUseCase (NUEVO)

**Archivo:** `src/domain/services/use_cases/business/auth/login/check_user_type_by_rol_use_case.py`

Este use case determina el tipo de usuario basándose en el **código del rol** asociado en `user_location_rol`. El rol es la **marca irrefutable** del tipo de usuario.

**Lógica de detección:**
| Rol Code | Tipo Usuario | is_internal |
|----------|--------------|-------------|
| `ADMIN` | Interno | `True` |
| `COLLA` | Interno | `True` |
| `USER` | Externo | `False` |

```python
from uuid import UUID
from typing import Optional
from pydantic import BaseModel
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.infrastructure.database.repositories.business.auth_repository import (
    AuthRepository,
)

# Códigos de roles internos
INTERNAL_ROL_CODES = ['ADMIN', 'COLLA']


class UserTypeInfo(BaseModel):
    """Información del tipo de usuario basada en su rol"""
    is_internal: bool
    rol_id: UUID
    rol_code: str


class CheckUserTypeByRolUseCase:
    def __init__(self):
        self.auth_repository = AuthRepository()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(self, config: Config, user_id: UUID) -> Optional[UserTypeInfo]:
        """
        Determina el tipo de usuario basándose en el código del rol.
        
        El ROL es la marca irrefutable del tipo de usuario:
        - ADMIN, COLLA → Usuario INTERNO
        - USER → Usuario EXTERNO
        
        Returns:
            UserTypeInfo con is_internal, rol_id y rol_code
            None si el usuario no tiene rol asignado (error)
        """
        # Obtener el rol del usuario desde user_location_rol
        user_rol = await self.auth_repository.get_user_rol_info(
            config=config, user_id=user_id
        )
        
        if user_rol is None:
            # Usuario sin rol asignado - esto no debería pasar
            return None
        
        # Determinar tipo basado en el código del rol
        is_internal = user_rol.rol_code in INTERNAL_ROL_CODES
        
        return UserTypeInfo(
            is_internal=is_internal,
            rol_id=user_rol.rol_id,
            rol_code=user_rol.rol_code
        )
```

**Query del repositorio:**

```python
# En AuthRepository

async def get_user_rol_info(
    self, config: Config, user_id: UUID
) -> Optional[UserRolInfo]:
    """
    Obtiene información del rol del usuario desde user_location_rol.
    Todos los usuarios (internos y externos) deben tener un registro aquí.
    """
    query = (
        config.session.query(
            UserLocationRolEntity.rol_id,
            RolEntity.code.label('rol_code')
        )
        .join(RolEntity, UserLocationRolEntity.rol_id == RolEntity.id)
        .filter(UserLocationRolEntity.user_id == user_id)
        .filter(UserLocationRolEntity.state == True)
    )
    result = await sync_to_async(query.first)()
    
    if result:
        return UserRolInfo(rol_id=result.rol_id, rol_code=result.rol_code)
    return None
```

### 3. AuthLoginExternalUseCase (NUEVO)

**Archivo:** `src/domain/services/use_cases/business/auth/login/auth_login_external_use_case.py`

```python
from typing import Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.access_token import AccessToken
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.core.classes.token import Token
from src.core.classes.async_message import Message

from src.domain.models.business.auth.login.auth_login_request import AuthLoginRequest
from src.domain.models.business.auth.login.auth_login_response import (
    AuthLoginResponse,
    PlatformConfiguration,
    PlatformVariations,
)
from src.domain.services.use_cases.business.auth.login.auth_initial_external_user_data_use_case import (
    AuthInitialExternalUserDataUseCase,
)
from src.domain.services.use_cases.business.auth.login.auth_external_rol_and_permissions_use_case import (
    AuthExternalRolAndPermissionsUseCase,
)
from src.domain.services.use_cases.business.auth.login.auth_menu_external_use_case import (
    AuthMenuExternalUseCase,
)
from src.domain.services.use_cases.business.auth.login.auth_languages_use_case import (
    AuthLanguagesUseCase,
)
from src.domain.models.entities.user.user_update import UserUpdate
from src.domain.services.use_cases.entities.user.user_update_use_case import (
    UserUpdateUseCase,
)
from src.infrastructure.database.repositories.entities.user_repository import (
    UserRepository,
)
from src.infrastructure.database.mappers.login_mapper import (
    map_to_user_login_response,
    map_to_currecy_login_response,
    map_to_language_login_response,
    map_to_platform_login_response,
    map_to_rol_login_response,
)


user_repository = UserRepository()

# ID fijo del rol USER
USER_ROL_ID = "1214ffde-997c-4482-b7fe-2524c828a188"


class AuthLoginExternalUseCase:
    def __init__(self):
        self.auth_initial_external_user_data_use_case = AuthInitialExternalUserDataUseCase()
        self.auth_external_rol_and_permissions_use_case = AuthExternalRolAndPermissionsUseCase()
        self.auth_menu_external_use_case = AuthMenuExternalUseCase()
        self.auth_languages_use_case = AuthLanguagesUseCase()
        self.user_update_use_case = UserUpdateUseCase(user_repository=user_repository)
        self.message = Message()
        self.token = Token()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: AuthLoginRequest,
        validated_user=None,  # Usuario ya validado por el orquestador
    ) -> Union[AuthLoginResponse, str, None]:
        config.response_type = RESPONSE_TYPE.OBJECT

        # 1. Obtener datos iniciales del usuario externo
        initial_data = await self.auth_initial_external_user_data_use_case.execute(
            config=config, email=params.email
        )
        if isinstance(initial_data, str):
            return initial_data

        platform_entity, user_entity, language_entity, currency_entity = initial_data

        # 2. Obtener rol USER y permisos
        rol_and_permissions = await self.auth_external_rol_and_permissions_use_case.execute(
            config=config
        )
        if isinstance(rol_and_permissions, str):
            return rol_and_permissions

        permissions, rol_entity = rol_and_permissions

        # 3. Obtener menú global filtrado por permisos del rol USER
        auth_menu = await self.auth_menu_external_use_case.execute(
            config=config, permissions=permissions
        )
        if isinstance(auth_menu, str):
            return auth_menu

        # 4. Obtener idiomas disponibles
        languages = await self.auth_languages_use_case.execute(config=config)
        if isinstance(languages, str):
            return languages

        # 5. Generar tokens
        access_token = AccessToken(
            rol_id=str(rol_entity.id),
            rol_code=str(rol_entity.code),
            user_id=str(user_entity.id),
            location_id=None,  # Usuario externo no tiene ubicación
            currency_id=str(currency_entity.id),
            company_id=None,   # Usuario externo no tiene compañía
            token_expiration_minutes=platform_entity.token_expiration_minutes,
            permissions=[permission.name for permission in permissions],
        )

        token = self.token.create_access_token(data=access_token)
        refresh_token = self.token.create_refresh_token(data=access_token)

        # 6. Actualizar refresh_token del usuario
        user_update = await self.user_update_use_case.execute(
            config=config,
            params=UserUpdate(
                id=user_entity.id,
                platform_id=user_entity.platform_id,
                password=user_entity.password,
                email=user_entity.email,
                identification=user_entity.identification,
                first_name=user_entity.first_name,
                last_name=user_entity.last_name,
                phone=user_entity.phone,
                refresh_token=refresh_token,
                state=user_entity.state,
            ),
        )

        if isinstance(user_update, str):
            return user_update

        # 7. Construir respuesta
        result = AuthLoginResponse(
            platform_configuration=PlatformConfiguration(
                user=map_to_user_login_response(user_entity=user_entity),
                currency=map_to_currecy_login_response(currency_entity=currency_entity),
                location=None,  # Usuario externo no tiene ubicación
                language=map_to_language_login_response(language_entity=language_entity),
                platform=map_to_platform_login_response(platform_entity=platform_entity),
                country=None,   # Usuario externo no tiene país
                company=None,   # Usuario externo no tiene compañía
                rol=map_to_rol_login_response(rol_entity=rol_entity),
                permissions=permissions,
                menu=auth_menu,
            ),
            platform_variations=PlatformVariations(
                currencies=[],   # Usuario externo no tiene monedas adicionales
                locations=[],    # Usuario externo no tiene ubicaciones
                languages=languages,
                companies=[],    # Usuario externo no tiene compañías
            ),
            token=token,
        )

        return result
```

### 4. Actualización de AuthMenuUseCase (Existente)

**Archivo:** `src/domain/services/use_cases/business/auth/login/auth_menu_use_case.py`

```python
# CAMBIO: Remover validación obligatoria de company (líneas 43-50)
# El use case ahora soporta company=None para el caso de menús externos
# aunque en la práctica para internos siempre tendrá valor

# El filtro por type se hace en el repositorio, no aquí
```

### 5. AuthMenuExternalUseCase (NUEVO)

**Archivo:** `src/domain/services/use_cases/business/auth/login/auth_menu_external_use_case.py`

```python
from typing import List, Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.login.auth_login_response import MenuLoginResponse
from src.infrastructure.database.repositories.business.auth_repository import AuthRepository
from src.infrastructure.database.repositories.business.mappers.auth.login.login_mapper import (
    map_to_menu_response,
)


class AuthMenuExternalUseCase:
    def __init__(self):
        self.auth_repository = AuthRepository()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        permissions: list,  # Lista de PermissionEntity del rol USER
    ) -> Union[List[MenuLoginResponse], str]:
        config.response_type = RESPONSE_TYPE.OBJECT

        # Obtener IDs de permisos
        permission_ids = [str(p.id) for p in permissions]

        # Obtener menús externos filtrados por permisos
        menus = await self.auth_repository.menu_external(
            config=config, permission_ids=permission_ids
        )

        if not menus:
            return []  # Retornar lista vacía, no error

        # Extraer y mapear menús únicos
        seen_menu_ids = set()
        result = []
        
        for menu_permission, menu_entity in menus:
            if menu_entity.id not in seen_menu_ids:
                seen_menu_ids.add(menu_entity.id)
                result.append(map_to_menu_response(menu_entity=menu_entity))

        return result
```

### 6. Actualización del Controller

**Archivo:** `src/infrastructure/web/controller/business/auth_controller.py`

```python
# Reemplazar en el método login:

async def login(self, config: Config, params: AuthLoginRequest) -> Response:
    # Ahora solo llama al orquestador
    result = await self.auth_login_orchestrator_use_case.execute(
        config=config, params=params
    )
    
    if isinstance(result, str):
        return Response.error(None, result)
    
    return Response.success_temporary_message(
        response=result,
        message=await self.message.get_message(
            config=config,
            message=MessageCoreEntity(
                key=KEYS_MESSAGES.CORE_SAVED_INFORMATION.value
            ),
        ),
    )
```

### 7. Nuevos Métodos en AuthRepository

**Archivo:** `src/infrastructure/database/repositories/business/auth_repository.py`

```python
# Agregar método para verificar user_location_rol

async def check_user_location_rol(
    self, config: Config, user_id: UUID
) -> Union[List, None]:
    async with config.async_db as db:
        stmt = (
            select(UserLocationRolEntity)
            .filter(UserLocationRolEntity.user_id == user_id)
            .filter(UserLocationRolEntity.state == True)
        )
        result = await db.execute(stmt)
        return result.scalars().all()


# Agregar método para obtener datos de usuario externo

async def initial_external_user_data(
    self, config: Config, email: str
) -> Union[Tuple[PlatformEntity, UserEntity, LanguageEntity, CurrencyEntity], None]:
    async with config.async_db as db:
        stmt = (
            select(PlatformEntity, UserEntity, LanguageEntity, CurrencyEntity)
            .join(PlatformEntity, PlatformEntity.id == UserEntity.platform_id)
            .join(LanguageEntity, LanguageEntity.id == PlatformEntity.language_id)
            .join(CurrencyEntity, CurrencyEntity.id == PlatformEntity.currency_id)
            .filter(UserEntity.email == email)
            .filter(UserEntity.state == True)
            .filter(PlatformEntity.location_id.is_(None))  # Solo usuarios externos
        )
        result = await db.execute(stmt)
        return result.first()


# Agregar método para obtener permisos del rol USER

async def external_rol_and_permissions(
    self, config: Config, rol_id: str
) -> Union[List[Tuple[RolEntity, RolPermissionEntity, PermissionEntity]], None]:
    async with config.async_db as db:
        stmt = (
            select(RolEntity, RolPermissionEntity, PermissionEntity)
            .join(RolPermissionEntity, RolPermissionEntity.rol_id == RolEntity.id)
            .join(PermissionEntity, PermissionEntity.id == RolPermissionEntity.permission_id)
            .filter(RolEntity.id == rol_id)
            .filter(RolEntity.state == True)
        )
        result = await db.execute(stmt)
        return result.all()


# Agregar método para obtener menú de usuarios internos (modificar existente)

async def menu(self, config: Config, params: Menu) -> Union[
    List[Tuple[MenuPermissionEntity, MenuEntity]], None
]:
    async with config.async_db as db:
        stmt = (
            select(MenuPermissionEntity, MenuEntity)
            .join(MenuPermissionEntity, MenuPermissionEntity.menu_id == MenuEntity.id)
            .filter(MenuEntity.company_id == params.company)
            .filter(MenuEntity.type == "INTERNAL")  # ← NUEVO: Seguridad
            .filter(MenuEntity.state == True)
        )
        result = await db.execute(stmt)
        return result.all()


# Agregar método para obtener menú de usuarios externos

async def menu_external(
    self, config: Config, permission_ids: List[str]
) -> Union[List[Tuple[MenuPermissionEntity, MenuEntity]], None]:
    async with config.async_db as db:
        stmt = (
            select(MenuPermissionEntity, MenuEntity)
            .join(MenuPermissionEntity, MenuPermissionEntity.menu_id == MenuEntity.id)
            .filter(MenuEntity.type == "EXTERNAL")  # ← Filtro por tipo
            .filter(MenuPermissionEntity.permission_id.in_(permission_ids))
            .filter(MenuEntity.state == True)
        )
        result = await db.execute(stmt)
        return result.all()
```

---

## Testing

### Estructura de Tests

```
tests/domain/services/use_cases/business/auth/login/
├── test_auth_login_orchestrator_use_case.py   # NUEVO
├── test_auth_login_external_use_case.py       # NUEVO
├── test_check_user_location_rol_use_case.py   # NUEVO
├── test_auth_login_use_case.py                # Existente
└── ...
```

### Test Cases Principales

```python
# test_auth_login_orchestrator_use_case.py

@pytest.mark.asyncio
async def test_login_internal_user_redirects_to_internal_flow():
    """Usuario con user_location_rol debe ir al flujo interno"""
    # Arrange: Usuario admin@empresa.com con user_location_rol
    # Act: Llamar al orquestador
    # Assert: Respuesta incluye company, location, menú de compañía

@pytest.mark.asyncio
async def test_login_external_user_redirects_to_external_flow():
    """Usuario con rol USER debe ir al flujo externo"""
    # Arrange: Usuario cliente@gmail.com con rol USER en user_location_rol (location_id=NULL)
    # Act: Llamar al orquestador
    # Assert: Respuesta tiene company=null, location=null, menú con type=EXTERNAL

@pytest.mark.asyncio
async def test_login_invalid_credentials_returns_error():
    """Credenciales inválidas deben retornar error genérico"""
    # Arrange: Email no existe o password incorrecto
    # Act: Llamar al orquestador
    # Assert: Retorna string de error

@pytest.mark.asyncio
async def test_external_user_gets_user_rol_permissions():
    """Usuario externo debe tener permisos del rol USER"""
    # Arrange: Usuario externo
    # Act: Login exitoso
    # Assert: permissions incluye MY_APPOINTMENTS

@pytest.mark.asyncio
async def test_external_user_gets_global_menu():
    """Usuario externo debe recibir menú con type=EXTERNAL"""
    # Arrange: Usuario externo con rol USER
    # Act: Login exitoso
    # Assert: menu incluye "Mis Citas" (/my-appointments) con type=EXTERNAL

@pytest.mark.asyncio
async def test_user_type_detection_based_on_rol_code():
    """La detección del tipo de usuario debe basarse en el código del rol"""
    # Arrange: 
    #   - Usuario 1 con rol ADMIN (code='ADMIN')
    #   - Usuario 2 con rol COLLA (code='COLLA') 
    #   - Usuario 3 con rol USER (code='USER')
    # Act: Llamar a CheckUserTypeByRolUseCase para cada usuario
    # Assert:
    #   - Usuario 1: is_internal=True, rol_code='ADMIN'
    #   - Usuario 2: is_internal=True, rol_code='COLLA'
    #   - Usuario 3: is_internal=False, rol_code='USER'

@pytest.mark.asyncio
async def test_create_external_user_registers_in_user_location_rol():
    """Al crear usuario externo, debe registrarse en user_location_rol con rol USER"""
    # Arrange: Datos de nuevo usuario externo
    # Act: Llamar a CreateUserExternalUseCase
    # Assert: 
    #   - Usuario creado en tabla user
    #   - Registro en user_location_rol con location_id=NULL y rol_id=USER

@pytest.mark.asyncio
async def test_create_external_user_registers_in_user_country():
    """Al crear usuario externo, debe registrarse en user_country"""
    # Arrange: Datos de nuevo usuario externo con country_id
    # Act: Llamar a CreateUserExternalUseCase
    # Assert: 
    #   - Usuario creado en tabla user
    #   - Registro en user_country con country_id especificado

@pytest.mark.asyncio
async def test_external_user_gets_country_in_response():
    """Usuario externo debe recibir su país en la respuesta de login"""
    # Arrange: Usuario externo con country asociado
    # Act: Login exitoso
    # Assert: platform_configuration.country contiene datos del país

@pytest.mark.asyncio
async def test_external_user_gets_all_currencies():
    """Usuario externo debe recibir todas las currencies disponibles"""
    # Arrange: Usuario externo
    # Act: Login exitoso
    # Assert: platform_variations.currencies contiene todas las monedas activas
```

---

## Fases de Implementación

### Fase 1: Base de Datos y Entidades ✅ COMPLETADA

**Objetivo:** Preparar la infraestructura de base de datos para soportar usuarios externos.

| # | Tarea | Archivo | Estado |
|---|-------|---------|--------|
| 1.1 | Migración menu type | `migrations/changelog-v47.sql` | ✅ |
| 1.2 | Migración user_location_rol | `migrations/changelog-v48.sql` | ✅ |
| 1.3 | Migración user_country | `migrations/changelog-v49.sql` | ✅ |
| 1.4 | Crear MenuType enum | `src/core/enums/menu_type.py` | ✅ |
| 1.5 | Actualizar MenuEntity | `src/infrastructure/database/entities/menu_entity.py` | ✅ |
| 1.6 | Actualizar UserLocationRolEntity | `src/infrastructure/database/entities/user_location_rol_entity.py` | ✅ |
| 1.7 | Crear UserCountryEntity | `src/infrastructure/database/entities/user_country_entity.py` | ✅ |
| 1.8 | Models Menu (type) | `src/domain/models/entities/menu/menu*.py` | ✅ |
| 1.9 | Mapper Menu (type) | `src/infrastructure/database/mappers/menu_mapper.py` | ✅ |
| 1.10 | Models UserCountry | `src/domain/models/entities/user_country/` | ✅ |
| 1.11 | Mapper UserCountry | `src/infrastructure/database/mappers/user_country_mapper.py` | ✅ |
| 1.12 | Interface IUserCountryRepository | `src/domain/services/repositories/entities/i_user_country_repository.py` | ✅ |
| 1.13 | Repository UserCountry | `src/infrastructure/database/repositories/entities/user_country_repository.py` | ✅ |
| 1.14 | Use Cases UserCountry | `src/domain/services/use_cases/entities/user_country/` | ✅ |

**Archivos creados/modificados:** 27 archivos (3 migraciones + 24 archivos de código)

**Entregable:** ✅ Migraciones creadas, entidades actualizadas, CRUD completo de UserCountry.

---

### Fase 2: Detección de Tipo de Usuario ✅ COMPLETADA

**Objetivo:** Implementar la lógica de detección basada en el rol.

| # | Tarea | Archivo | Estado |
|---|-------|---------|--------|
| 2.1 | Crear modelo UserTypeInfo | `src/domain/models/business/auth/login/user_type_info.py` | ✅ |
| 2.2 | Crear modelo UserRolInfo | `src/domain/models/business/auth/login/user_type_info.py` | ✅ |
| 2.3 | Agregar query al repositorio | `src/infrastructure/database/repositories/business/auth_repository.py` | ✅ |
| 2.4 | Crear CheckUserTypeByRolUseCase | `src/domain/services/use_cases/business/auth/login/check_user_type_by_rol_use_case.py` | ✅ |
| 2.5 | Actualizar index exports | `src/domain/models/business/auth/login/index.py` | ✅ |

**Lógica implementada:**
- `ADMIN`, `COLLA` → `is_internal = True` (Usuario INTERNO)
- `USER` → `is_internal = False` (Usuario EXTERNO)

**Entregable:** ✅ Detección por rol funcionando.

---

### Fase 3: Flujo de Login Externo ✅ COMPLETADA

**Objetivo:** Implementar el flujo completo de login para usuarios externos.

| # | Tarea | Archivo | Estado |
|---|-------|---------|--------|
| 3.1 | Crear AuthLoginOrchestratorUseCase | `src/domain/services/use_cases/business/auth/login/auth_login_orchestrator_use_case.py` | ✅ |
| 3.2 | Crear AuthLoginExternalUseCase | `src/domain/services/use_cases/business/auth/login/auth_login_external_use_case.py` | ✅ |
| 3.3 | Crear AuthInitialExternalUserDataUseCase | `src/domain/services/use_cases/business/auth/login/auth_initial_external_user_data_use_case.py` | ✅ |
| 3.4 | Crear AuthExternalRolAndPermissionsUseCase | `src/domain/services/use_cases/business/auth/login/auth_external_rol_and_permissions_use_case.py` | ✅ |
| 3.5 | Crear AuthMenuExternalUseCase | `src/domain/services/use_cases/business/auth/login/auth_menu_external_use_case.py` | ✅ |
| 3.6 | Crear AuthCurrenciesExternalUseCase | `src/domain/services/use_cases/business/auth/login/auth_currencies_external_use_case.py` | ✅ |
| 3.7 | Agregar queries al repositorio | `src/infrastructure/database/repositories/business/auth_repository.py` | ✅ |
| 3.8 | Actualizar AuthController | `src/infrastructure/web/controller/business/auth_controller.py` | ✅ |
| 3.9 | Tests de integración | `test_login_external.py` | ⏳ Pendiente |

**Archivos creados:**
- `auth_login_orchestrator_use_case.py`: Orquestador que detecta tipo de usuario y redirige
- `auth_login_external_use_case.py`: Flujo completo de login externo
- `auth_initial_external_user_data_use_case.py`: Obtiene datos iniciales (platform, user, language, currency)
- `auth_external_rol_and_permissions_use_case.py`: Obtiene rol USER y permisos
- `auth_menu_external_use_case.py`: Obtiene menús con type='EXTERNAL'
- `auth_currencies_external_use_case.py`: Obtiene todas las currencies globales

**Métodos agregados al repositorio:**
- `initial_external_user_data()`: Datos de usuario externo (sin location/company)
- `external_rol_and_permissions()`: Permisos del rol USER
- `menu_external()`: Menús externos filtrados por permisos
- `all_currencies()`: Todas las currencies activas

**Entregable:** ✅ Login externo implementado.

---

### Fase 4: Flujo de Refresh Token Externo ✅ COMPLETADA

**Objetivo:** Implementar refresh token para usuarios externos.

| # | Tarea | Archivo | Estado |
|---|-------|---------|--------|
| 4.1 | Crear AuthRefreshTokenOrchestratorUseCase | `src/domain/services/use_cases/business/auth/login/auth_refresh_token_orchestrator_use_case.py` | ✅ |
| 4.2 | Crear AuthRefreshTokenExternalUseCase | `src/domain/services/use_cases/business/auth/login/auth_refresh_token_external_use_case.py` | ✅ |
| 4.3 | Actualizar AuthController | `src/infrastructure/web/controller/business/auth_controller.py` | ✅ |
| 4.4 | Tests | `test_refresh_token_external.py` | ⏳ Pendiente |

**Archivos creados:**
- `auth_refresh_token_orchestrator_use_case.py`: Detecta tipo de usuario por rol y redirige
- `auth_refresh_token_external_use_case.py`: Flujo completo de refresh token para externos

**Lógica implementada:**
- Usa `CheckUserTypeByRolUseCase` para detectar tipo de usuario
- Usuarios internos → `AuthRefreshTokenUseCase`
- Usuarios externos → `AuthRefreshTokenExternalUseCase`

**Entregable:** ✅ Refresh token funcionando para externos.

---

### Fase 5: Registro de Usuario Externo ✅ COMPLETADA

**Objetivo:** Actualizar el flujo de creación de usuarios externos.

| # | Tarea | Archivo | Estado |
|---|-------|---------|--------|
| 5.1 | Actualizar CreateUserExternalRequest | `src/domain/models/business/auth/create_user_external/create_user_external_request.py` | ✅ |
| 5.2 | Modificar CreateUserExternalUseCase | `src/domain/services/use_cases/business/auth/create_user_external/create_user_external_use_case.py` | ✅ |
| 5.3 | Actualizar DeleteUserExternalUseCase | `src/domain/services/use_cases/business/auth/delete_user_external/delete_user_external_use_case.py` | ✅ |
| 5.4 | Agregar delete_by_user_id al repositorio | `src/infrastructure/database/repositories/entities/user_location_rol_repository.py` | ✅ |
| 5.5 | Tests | `test_create_user_external.py` | ⏳ Pendiente |

**Cambios realizados:**

1. **CreateUserExternalRequest**: Agregado campo `country_id` opcional
2. **CreateUserExternalUseCase**:
   - Valida `country_id` si se proporciona
   - Busca el rol USER por código usando `ROL_TYPE.USER`
   - Crea registro en `user_location_rol` con `location_id=None` y rol USER
   - Crea registro en `user_country` si se proporciona `country_id`
3. **DeleteUserExternalUseCase**:
   - Elimina registro de `user_location_rol` antes de eliminar usuario
   - Elimina registro de `user_country` antes de eliminar usuario
4. **UserLocationRolRepository**: Agregado método `delete_by_user_id`

**Entregable:** ✅ Registro completo de usuarios externos.

---

### Fase 6: Menú y Seguridad ✅ COMPLETADA

**Objetivo:** Implementar filtrado seguro de menús.

| # | Tarea | Archivo | Estado |
|---|-------|---------|--------|
| 6.1 | Actualizar método menu en AuthRepository | `src/infrastructure/database/repositories/business/auth_repository.py` | ✅ |
| 6.2 | Actualizar CreateCompanyUseCase | `src/domain/services/use_cases/business/auth/create_company/create_company_use_case.py` | ✅ |
| 6.3 | Actualizar CloneMenusForCompanyUseCase | `src/domain/services/use_cases/business/auth/create_company/clone_menus_for_company_use_case.py` | ✅ |
| 6.4 | Tests de seguridad | `test_menu_security.py` | ⏳ Pendiente |

**Cambios realizados:**

1. **AuthRepository.menu()**: 
   - Agregado filtro `MenuEntity.type == "INTERNAL"` para seguridad
   - Agregado filtro `MenuEntity.state == True`
   - Los menús EXTERNAL nunca se retornan a usuarios internos

2. **CreateCompanyUseCase**:
   - Filtro de template_menus ahora incluye `type = 'INTERNAL'`
   - Solo se clonan menús internos, los externos son globales

3. **CloneMenusForCompanyUseCase**:
   - Se preserva el campo `type` al clonar menús

**Seguridad implementada:**
- Usuarios INTERNOS solo ven menús con `type = 'INTERNAL'`
- Usuarios EXTERNOS solo ven menús con `type = 'EXTERNAL'`
- Al crear compañías, solo se clonan menús INTERNAL

**Entregable:** ✅ Menús filtrados correctamente.

---

### Fase 7: Testing y QA

**Objetivo:** Validación completa del sistema.

| # | Tarea | Descripción |
|---|-------|-------------|
| 7.1 | Tests unitarios | Cobertura > 80% en nuevos use cases |
| 7.2 | Tests de integración | Flujos completos E2E |
| 7.3 | Tests de regresión | Verificar que internos siguen funcionando |
| 7.4 | Tests de seguridad | Verificar aislamiento de datos |
| 7.5 | Documentación | Actualizar docs de API |

**Entregable:** Sistema validado y documentado.

---

### Resumen de Fases

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FASES DE IMPLEMENTACIÓN                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  FASE 1 ✅      FASE 2 ✅      FASE 3         FASE 4         FASE 5        │
│  ┌─────┐        ┌─────┐        ┌─────┐        ┌─────┐        ┌─────┐       │
│  │ DB  │───────▶│Detect│───────▶│Login│───────▶│Refr.│───────▶│Regis│       │
│  │ ✅  │        │ ✅   │        │ Ext │        │Token│        │ Ext │       │
│  └─────┘        └─────┘        └─────┘        └─────┘        └─────┘       │
│     │                                                            │          │
│     │              FASE 6                    FASE 7              │          │
│     │              ┌─────┐                   ┌─────┐             │          │
│     └─────────────▶│Menu │──────────────────▶│ QA  │◀────────────┘          │
│                    │ Sec │                   │     │                        │
│                    └─────┘                   └─────┘                        │
│                                                                              │
│  Estado actual: FASE 1 ✅ y FASE 2 ✅ COMPLETADAS                           │
│                                                                              │
│  Dependencias:                                                               │
│  • Fase 3 depende de Fase 2 (detección) ← DESBLOQUEADA                      │
│  • Fase 4 depende de Fase 2 (detección) ← DESBLOQUEADA                      │
│  • Fase 5 depende de Fase 1 (entidades) ← DESBLOQUEADA                      │
│  • Fase 6 depende de Fase 1 (campo type) ← DESBLOQUEADA                     │
│  • Fase 7 depende de todas las anteriores                                   │
│                                                                              │
│  Próximas fases posibles: 3, 4, 5, 6 (en paralelo)                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Historial de Cambios

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0 | Dic 2024 | Creación inicial del flujo Login | Equipo de Desarrollo Goluti |
| 2.0 | Ene 2026 | **Refactor completo**: Implementación de arquitectura con orquestador para soportar usuarios internos y externos. Nuevo `AuthLoginOrchestratorUseCase` que detecta tipo de usuario y redirige al flujo correspondiente. Nuevos use cases: `CheckUserLocationRolUseCase`, `AuthLoginExternalUseCase`, `AuthInitialExternalUserDataUseCase`, `AuthExternalRolAndPermissionsUseCase`, `AuthMenuExternalUseCase`. Soporte para rol USER con permisos MY_APPOINTMENTS y menú global. | Equipo de Desarrollo Goluti |
| 2.1 | Ene 2026 | **Campo `type` en tabla menu**: Se agrega columna `type` (INTERNAL/EXTERNAL/BOTH) a la tabla `menu` para filtrado seguro de menús. Los menús internos se filtran por `type = 'INTERNAL'` además de `company_id`. Los menús externos se filtran únicamente por `type = 'EXTERNAL'`. Se incluye migración `changelog-v47.sql`, enum `MENU_TYPE`, actualización de `MenuEntity` y queries del repositorio. **Impacto en Create Company**: La clonación de menús ahora solo clona menús con `type = 'INTERNAL'`. | Equipo de Desarrollo Goluti |
| 2.2 | Ene 2026 | **Detección de tipo por ROL**: La detección del tipo de usuario ahora se basa en el **código del rol** (marca irrefutable) en lugar de la existencia o ausencia de `location_id`. `CheckUserLocationRolUseCase` renombrado a `CheckUserTypeByRolUseCase`. Lógica: `ADMIN`/`COLLA` = interno, `USER` = externo. **Centralización en user_location_rol**: Todos los usuarios (internos y externos) ahora tienen registro en `user_location_rol`. Para externos, `location_id = NULL`. Migración `changelog-v48.sql` hace `location_id` nullable y agrega índice parcial. **Casos de uso afectados**: Se documenta el impacto completo incluyendo `AuthRefreshTokenUseCase` (crítico - requiere orquestador), `DeleteUserExternalUseCase` (eliminar registro de `user_location_rol`), y `AuthController` (usar orquestadores). Se agregan nuevos use cases: `AuthRefreshTokenOrchestratorUseCase`, `AuthRefreshTokenExternalUseCase`. | Equipo de Desarrollo Goluti |
| 2.3 | Ene 2026 | **Tabla user_country**: Nueva tabla para asociar país a usuarios externos. Migración `changelog-v49.sql`. Actualización de `CreateUserExternalRequest` para incluir `country_id`. Respuesta de login ahora incluye `country` para externos. **Currencies globales**: `platform_variations.currencies` ahora retorna todas las monedas disponibles de la tabla `currency` para usuarios externos. **Fases de implementación**: Se agregan 7 fases detalladas con tareas específicas, archivos a crear/modificar y entregables. Diagrama de dependencias entre fases. | Equipo de Desarrollo Goluti |
| 2.4 | Ene 2026 | **FASE 1 COMPLETADA ✅**: Implementación de toda la infraestructura de base de datos. **Migraciones**: `changelog-v47.sql` (campo type en menu), `changelog-v48.sql` (location_id nullable), `changelog-v49.sql` (tabla user_country). **Entidades**: `MenuEntity` actualizada con campo `type`, `UserLocationRolEntity` con `location_id` nullable, nueva `UserCountryEntity`. **CRUD completo UserCountry**: Models, Mapper, Interface Repository, Repository (con métodos adicionales `read_by_user_id` y `delete_by_user_id`), 5 Use Cases. **Enum**: `MENU_TYPE` (INTERNAL/EXTERNAL). Total: 27 archivos creados/modificados. | Equipo de Desarrollo Goluti |
| 2.5 | Ene 2026 | **FASE 2 COMPLETADA ✅**: Implementación de detección de tipo de usuario por rol. **Modelos**: `UserTypeInfo` (is_internal, rol_id, rol_code), `UserRolInfo` (rol_id, rol_code). **Use Case**: `CheckUserTypeByRolUseCase` con lógica ADMIN/COLLA = interno, USER = externo. **Repository**: Método `get_user_rol_info` agregado a `AuthRepository` para consultar rol desde `user_location_rol`. Total: 4 archivos creados/modificados. | Equipo de Desarrollo Goluti |
| 2.6 | Ene 23, 2026 | **Migración de `country` a `geo_division`**: Tabla `country` eliminada y reemplazada por `geo_division` jerárquica. `CountryEntity` → `GeoDivisionEntity` en toda la lógica de auth (repository, mapper, use cases). Response de login: `LocationLoginResponse` ahora incluye `city_id`, `latitude`, `longitude`, `google_place_id` en vez de `city` (string). `CountryLoginResponse` ahora se mapea desde `GeoDivisionEntity` (tipo COUNTRY). `user_country.country_id` ahora referencia `geo_division(id)`. Diagramas y ejemplos actualizados. | Equipo de Desarrollo Goluti |

---

*Documento generado para el proyecto Goluti Platform*

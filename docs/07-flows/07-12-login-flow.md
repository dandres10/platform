# 07-12: Flujo de Autenticación (Login)

## Información del Documento

| Campo | Detalle |
|-------|---------|
| **Versión** | 1.0 |
| **Última Actualización** | Diciembre 2024 |
| **Autor** | Equipo de Desarrollo Goluti |
| **Estado** | Activo |

---

## Resumen Ejecutivo

Este documento especifica el flujo de autenticación (login) del sistema. El endpoint permite a los usuarios internos y externos autenticarse proporcionando sus credenciales y recibiendo un token JWT junto con la configuración completa de la plataforma.

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

Autenticar usuarios en el sistema mediante email y contraseña, generando tokens JWT para acceso a recursos protegidos y proporcionando la configuración inicial de la plataforma.

### Alcance

- Validación de credenciales (email y contraseña)
- Generación de access token y refresh token
- Obtención de configuración de plataforma del usuario
- Obtención de variaciones disponibles (monedas, ubicaciones, idiomas, compañías)
- Obtención de menú según permisos del rol

### Características

| Característica | Descripción |
|----------------|-------------|
| Autenticación | Email + Contraseña hasheada |
| Token | JWT con expiración configurable |
| Refresh Token | Token de renovación almacenado en BD |
| Multi-compañía | Usuario puede pertenecer a múltiples compañías |
| Multi-ubicación | Usuario puede tener acceso a múltiples ubicaciones |

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

### Request Body

```json
{
  "email": "usuario@goluti.com",
  "password": "SecurePassword123!"
}
```

### Response

**Éxito (200 OK):**
```json
{
  "data": {
    "platform_configuration": {
      "user": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "usuario@goluti.com",
        "first_name": "Juan",
        "last_name": "Pérez",
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
        "city": "Bogotá",
        "phone": "+573001234567",
        "email": "sede@goluti.com",
        "main_location": true,
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
        {
          "id": "dd0e8400-e29b-41d4-a716-446655440000",
          "name": "READ",
          "description": "Permiso de lectura",
          "state": true
        },
        {
          "id": "ee0e8400-e29b-41d4-a716-446655440000",
          "name": "SAVE",
          "description": "Permiso de creación",
          "state": true
        }
      ],
      "menu": [
        {
          "id": "ff0e8400-e29b-41d4-a716-446655440000",
          "name": "dashboard",
          "label": "Dashboard",
          "description": "Panel principal",
          "top_id": "00000000-0000-0000-0000-000000000000",
          "route": "/dashboard",
          "state": true,
          "icon": "home"
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

**Error (400 Bad Request):**
```json
{
  "data": null,
  "message": "Registro no encontrado para eliminar",
  "notification_type": "error",
  "message_type": "temporary"
}
```

---

## Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────────┐
│                         LOGIN FLOW                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. VALIDAR USUARIO                                               │
│    - AuthValidateUserUseCase                                     │
│    - Buscar usuario por email                                    │
│    - Verificar contraseña con hash                               │
│    - Si falla → Error credenciales inválidas                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. OBTENER COMPAÑÍAS DEL USUARIO                                 │
│    - CompaniesByUserUseCase                                      │
│    - Lista de compañías a las que pertenece el usuario           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. OBTENER DATOS INICIALES DEL USUARIO                          │
│    - AuthInitialUserDataUseCase                                  │
│    - Platform, User, Language, Location, Currency, Country,      │
│      Company                                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. OBTENER ROL Y PERMISOS                                        │
│    - AuthUserRoleAndPermissionsUseCase                           │
│    - Rol del usuario en la ubicación                             │
│    - Lista de permisos asociados al rol                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. OBTENER MENÚ                                                  │
│    - AuthMenuUseCase                                             │
│    - Menús de la compañía filtrados por permisos                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. OBTENER VARIACIONES DE PLATAFORMA                            │
│    - AuthCurrenciesUseCase → Monedas disponibles                 │
│    - AuthLocationsUseCase → Ubicaciones del usuario              │
│    - AuthLanguagesUseCase → Idiomas disponibles                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. GENERAR TOKENS                                                │
│    - Crear AccessToken con datos del usuario                     │
│    - Crear RefreshToken                                          │
│    - Actualizar refresh_token en tabla user                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. RETORNAR RESPUESTA                                            │
│    - platform_configuration: Configuración actual                │
│    - platform_variations: Opciones disponibles                   │
│    - token: JWT de acceso                                        │
└─────────────────────────────────────────────────────────────────┘
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
    location: LocationLoginResponse = Field(...)
    language: LanguageLoginResponse = Field(...)
    platform: PlatformLoginResponse = Field(...)
    country: CountryLoginResponse = Field(...)
    company: CompanyLoginResponse = Field(...)
    rol: RolLoginResponse = Field(...)
    permissions: List[PermissionLoginResponse] = Field(...)
    menu: List[MenuLoginResponse] = Field(...)
```

#### PlatformVariations

```python
class PlatformVariations(BaseModel):
    currencies: List[CurrencyLoginResponse] = Field(...)
    locations: List[LocationLoginResponse] = Field(...)
    languages: List[LanguageLoginResponse] = Field(...)
    companies: List[CompanyLoginResponse] = Field(...)
```

#### Sub-modelos de Respuesta

```python
class UserLoginResponse(BaseModel):
    id: UUID4 = Field(...)
    email: str = Field(..., max_length=255)
    first_name: str = Field(..., max_length=255)
    last_name: str = Field(..., max_length=255)
    phone: str = Field(..., max_length=20)
    state: bool = Field(...)

class CurrencyLoginResponse(BaseModel):
    id: UUID4 = Field(...)
    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=10)
    symbol: str = Field(..., max_length=10)
    state: bool = Field(...)

class LocationLoginResponse(BaseModel):
    id: UUID4 = Field(...)
    name: str = Field(..., max_length=255)
    address: str = Field(...)
    city: str = Field(..., max_length=100)
    phone: str = Field(..., max_length=20)
    email: str = Field(..., max_length=100)
    main_location: bool = Field(...)
    state: bool = Field(...)

class LanguageLoginResponse(BaseModel):
    id: UUID4 = Field(...)
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=10)
    native_name: str = Field(..., max_length=100)
    state: bool = Field(...)

class PlatformLoginResponse(BaseModel):
    id: UUID4 = Field(...)
    language_id: UUID4 = Field(...)
    location_id: UUID4 = Field(...)
    token_expiration_minutes: int = Field(...)
    currency_id: UUID4 = Field(...)

class CountryLoginResponse(BaseModel):
    id: UUID4 = Field(...)
    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=10)
    phone_code: str = Field(..., max_length=10)
    state: bool = Field(...)

class CompanyLoginResponse(BaseModel):
    id: UUID4 = Field(...)
    name: str = Field(..., max_length=255)
    inactivity_time: int = Field(...)
    nit: str = Field(..., max_length=255)
    state: bool = Field(...)

class RolLoginResponse(BaseModel):
    id: UUID4 = Field(...)
    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=255)
    description: str = Field(...)
    state: bool = Field(...)

class PermissionLoginResponse(BaseModel):
    id: UUID4 = Field(...)
    name: str = Field(..., max_length=255)
    description: str = Field(...)
    state: bool = Field(...)

class MenuLoginResponse(BaseModel):
    id: UUID4 = Field(...)
    name: str = Field(..., max_length=100)
    label: str = Field(..., max_length=300)
    description: str = Field(..., max_length=300)
    top_id: UUID4 = Field(...)
    route: str = Field(..., max_length=300)
    state: bool = Field(default=True)
    icon: str = Field(..., max_length=50)
```

---

## Casos de Uso

### Caso de Uso Principal: AuthLoginUseCase

Orquesta todo el flujo de login combinando múltiples casos de uso auxiliares.

### Casos de Uso Auxiliares

| Use Case | Descripción |
|----------|-------------|
| `AuthValidateUserUseCase` | Valida email y contraseña del usuario |
| `CompaniesByUserUseCase` | Obtiene compañías a las que pertenece el usuario |
| `AuthInitialUserDataUseCase` | Obtiene datos iniciales (platform, user, language, etc.) |
| `AuthUserRoleAndPermissionsUseCase` | Obtiene rol y permisos del usuario en la ubicación |
| `AuthMenuUseCase` | Obtiene menú filtrado por permisos |
| `AuthCurrenciesUseCase` | Obtiene monedas disponibles en la ubicación |
| `AuthLocationsUseCase` | Obtiene ubicaciones del usuario en la compañía |
| `AuthLanguagesUseCase` | Obtiene idiomas disponibles |

---

## Validaciones

### Reglas de Negocio

1. **Email Existe**: El email debe existir en la tabla `user`
2. **Contraseña Válida**: La contraseña debe coincidir con el hash almacenado
3. **Usuario Activo**: El usuario debe tener `state = true`
4. **Configuración Completa**: El usuario debe tener platform, ubicación, y rol asignados

### Validaciones Técnicas

#### 1. Validación de Usuario

```python
# Buscar usuario por email
result_users_list = await self.user_list_use_case.execute(
    config=config,
    params=Pagination(
        all_data=True,
        filters=[
            FilterManager(
                field="email",
                condition=CONDITION_TYPE.EQUALS.value,
                value=params.email,
            )
        ],
    ),
)

# Verificar contraseña
check_password = self.password.check_password(
    password=params.password, 
    hashed_password=user.password
)
```

---

## Códigos de Error

### Escenarios de Error

| Escenario | Mensaje |
|-----------|---------|
| Email no encontrado | "Registro no encontrado" |
| Contraseña incorrecta | "Registro no encontrado" |
| Usuario inactivo | "Registro no encontrado" |
| Sin configuración de platform | Error de datos iniciales |
| Sin rol asignado | Error de permisos |

**Nota**: Por seguridad, los errores de autenticación retornan un mensaje genérico para no revelar información sobre usuarios existentes.

---

## Seguridad

### Consideraciones de Seguridad

1. **Contraseñas Hasheadas**: Las contraseñas se almacenan con hash bcrypt
2. **Tokens JWT**: Tokens firmados con algoritmo HS256
3. **Refresh Token**: Almacenado en BD para invalidación
4. **Sin Decoradores de Permisos**: Endpoint público (pre-autenticación)
5. **Mensajes Genéricos**: No revelar si el email existe

### Estructura del Token JWT

```python
class AccessToken(BaseModel):
    rol_id: str
    rol_code: str
    user_id: str
    location_id: str
    currency_id: str
    company_id: str
    token_expiration_minutes: int
    permissions: List[str]
```

### Configuración de Tokens

| Token | Expiración | Almacenamiento |
|-------|------------|----------------|
| Access Token | Configurable (default: 60 min) | Cliente |
| Refresh Token | Configurable (default: 1440 min) | BD (tabla user) |

---

## Ejemplos

### Ejemplo 1: Login Exitoso

**Request:**
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@goluti.com",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "data": {
    "platform_configuration": {
      "user": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "admin@goluti.com",
        "first_name": "Admin",
        "last_name": "Goluti",
        "phone": "+573001234567",
        "state": true
      },
      "rol": {
        "id": "cc0e8400-e29b-41d4-a716-446655440000",
        "name": "Administrador",
        "code": "ADMIN",
        "description": "Rol de administrador",
        "state": true
      },
      "permissions": [
        {"id": "...", "name": "READ", "description": "Lectura", "state": true},
        {"id": "...", "name": "SAVE", "description": "Creación", "state": true},
        {"id": "...", "name": "UPDATE", "description": "Actualización", "state": true},
        {"id": "...", "name": "DELETE", "description": "Eliminación", "state": true}
      ],
      ...
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

### Ejemplo 2: Error - Email No Encontrado

**Request:**
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "noexiste@goluti.com",
  "password": "cualquierpassword"
}
```

**Response:**
```json
{
  "data": null,
  "message": "Registro no encontrado para eliminar",
  "notification_type": "error",
  "message_type": "temporary"
}
```

### Ejemplo 3: Error - Contraseña Incorrecta

**Request:**
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@goluti.com",
  "password": "contraseñaincorrecta"
}
```

**Response:**
```json
{
  "data": null,
  "message": "Registro no encontrado para eliminar",
  "notification_type": "error",
  "message_type": "temporary"
}
```

---

## Flujo de Datos

### Entidades Involucradas

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
       └────────────▶│   COMPANY    │────▶│   COUNTRY    │
                     └──────────────┘     └──────────────┘
                            │
                            ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│USER_LOC_ROL  │────▶│     ROL      │────▶│ ROL_PERMISSION│
└──────────────┘     └──────────────┘     └──────────────┘
                                                │
                                                ▼
                                         ┌──────────────┐
                                         │  PERMISSION  │
                                         └──────────────┘
```

### Tablas Consultadas

| Tabla | Propósito |
|-------|-----------|
| `user` | Validar credenciales, obtener datos del usuario |
| `platform` | Configuración de plataforma del usuario |
| `language` | Idioma preferido |
| `location` | Ubicación principal y disponibles |
| `currency` | Moneda principal y disponibles |
| `company` | Compañía actual y disponibles |
| `country` | País de la ubicación |
| `user_location_rol` | Relación usuario-ubicación-rol |
| `rol` | Rol del usuario |
| `rol_permission` | Relación rol-permisos |
| `permission` | Permisos del rol |
| `menu` | Menús de la compañía |
| `menu_permission` | Relación menú-permisos |

---

## Historial de Cambios

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0 | Dic 2024 | Creación inicial del flujo Login | Equipo de Desarrollo Goluti |

---

*Documento generado para el proyecto Goluti Platform*


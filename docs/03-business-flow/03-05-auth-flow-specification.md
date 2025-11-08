# Especificación del Flujo de Autenticación (Auth Flow)

**Versión**: 1.0  
**Fecha**: Noviembre 2024  
**Estado**: Vigente  
**Autor(es)**: Equipo de Desarrollo Goluti

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Operaciones Disponibles](#operaciones-disponibles)
3. [Login - Especificación Completa](#login---especificación-completa)
4. [Refresh Token](#refresh-token)
5. [Logout](#logout)
6. [Create API Token](#create-api-token)
7. [Seguridad](#seguridad)
8. [Referencias](#referencias)

---

## Introducción

El módulo de autenticación (`auth`) es el componente central de seguridad del sistema. Implementa autenticación basada en **JWT (JSON Web Tokens)** y proporciona operaciones para gestión de sesiones de usuario.

### Características Principales

- Autenticación mediante email y contraseña
- Generación de Access Token (JWT) y Refresh Token
- Carga de configuración inicial del usuario
- Renovación de tokens sin re-login
- Cierre de sesión con invalidación de refresh token
- Generación de tokens de API para integraciones

---

## Operaciones Disponibles

| Operación | Endpoint | Método | Auth Requerida |
|-----------|----------|--------|----------------|
| **Login** | `/auth/login` | POST | ❌ No |
| **Refresh Token** | `/auth/refresh_token` | POST | ✅ Sí |
| **Logout** | `/auth/logout` | POST | ✅ Sí |
| **Create API Token** | `/auth/create-api-token` | POST | ✅ Sí |

---

## Login - Especificación Completa

### Endpoint

```
POST /auth/login
```

### Request

**Headers:**
```
Content-Type: application/json
Language: es | en
```

**Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123",
  "company_id": "uuid-opcional"  // Opcional: Empresa específica
}
```

**Modelo Pydantic:**
```python
class AuthLoginRequest(BaseModel):
    email: EmailStr
    password: str
    company_id: Optional[UUID4] = None
```

### Response

**Success (200):**
```json
{
  "message_type": "temporary",
  "notification_type": "success",
  "message": "Inicio de sesión exitoso",
  "response": {
    "platform_configuration": {
      "user": {
        "id": "uuid",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890",
        "identification": "12345678"
      },
      "currency": {
        "id": "uuid",
        "code": "USD",
        "name": "US Dollar",
        "symbol": "$"
      },
      "location": {
        "id": "uuid",
        "name": "Headquarters",
        "address": "123 Main St"
      },
      "language": {
        "id": "uuid",
        "code": "en",
        "name": "English"
      },
      "platform": {
        "id": "uuid",
        "token_expiration_minutes": 60,
        "refresh_token_expiration_minutes": 1440
      },
      "country": {
        "id": "uuid",
        "code": "US",
        "name": "United States"
      },
      "company": {
        "id": "uuid",
        "name": "Acme Corp",
        "nit": "123456789"
      },
      "rol": {
        "id": "uuid",
        "code": "ADMIN",
        "name": "Administrator"
      },
      "permissions": [
        {
          "id": "uuid",
          "name": "save",
          "code": "SAVE"
        },
        {
          "id": "uuid",
          "name": "update",
          "code": "UPDATE"
        }
        // ... más permisos
      ],
      "menu": [
        {
          "id": "uuid",
          "name": "Dashboard",
          "icon": "dashboard",
          "route": "/dashboard",
          "order": 1
        }
        // ... más elementos de menú
      ]
    },
    "platform_variations": {
      "currencies": [
        /* Lista de monedas disponibles */
      ],
      "locations": [
        /* Lista de ubicaciones del usuario */
      ],
      "languages": [
        /* Lista de idiomas disponibles */
      ],
      "companies": [
        /* Lista de empresas del usuario */
      ]
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Error - Credenciales Inválidas (200):**
```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "Email o contraseña incorrectos",
  "response": null
}
```

### Diagrama de Secuencia

```
┌────────┐         ┌──────────┐         ┌──────────────┐         ┌──────────────┐
│Cliente │         │  Router  │         │  Controller  │         │   UseCase    │
└───┬────┘         └────┬─────┘         └──────┬───────┘         └──────┬───────┘
    │                   │                       │                        │
    │ POST /auth/login  │                       │                        │
    ├──────────────────>│                       │                        │
    │                   │                       │                        │
    │             Valida Request                │                        │
    │                   ├──────────────────────>│                        │
    │                   │                       │                        │
    │                   │                Invoca login()                  │
    │                   │                       ├───────────────────────>│
    │                   │                       │                        │
    │                   │                       │         1. Validar Credenciales
    │                   │                       │         ├──────────────┐
    │                   │                       │         │ ValidateUser │
    │                   │                       │         │<─────────────┘
    │                   │                       │                        │
    │                   │                       │         2. Obtener Empresas
    │                   │                       │         ├──────────────┐
    │                   │                       │         │CompaniesUser │
    │                   │                       │         │<─────────────┘
    │                   │                       │                        │
    │                   │                       │         3. Cargar Datos Iniciales
    │                   │                       │         ├──────────────┐
    │                   │                       │         │InitialData   │
    │                   │                       │         │<─────────────┘
    │                   │                       │                        │
    │                   │                       │         4. Obtener Rol y Permisos
    │                   │                       │         ├──────────────┐
    │                   │                       │         │RolePermiss   │
    │                   │                       │         │<─────────────┘
    │                   │                       │                        │
    │                   │                       │         5. Construir Menú
    │                   │                       │         ├──────────────┐
    │                   │                       │         │BuildMenu     │
    │                   │                       │         │<─────────────┘
    │                   │                       │                        │
    │                   │                       │         6. Obtener Monedas
    │                   │                       │         ├──────────────┐
    │                   │                       │         │GetCurrencies │
    │                   │                       │         │<─────────────┘
    │                   │                       │                        │
    │                   │                       │         7. Obtener Ubicaciones
    │                   │                       │         ├──────────────┐
    │                   │                       │         │GetLocations  │
    │                   │                       │         │<─────────────┘
    │                   │                       │                        │
    │                   │                       │         8. Obtener Idiomas
    │                   │                       │         ├──────────────┐
    │                   │                       │         │GetLanguages  │
    │                   │                       │         │<─────────────┘
    │                   │                       │                        │
    │                   │                       │         9. Generar Tokens JWT
    │                   │                       │         ├──────────────┐
    │                   │                       │         │CreateTokens  │
    │                   │                       │         │<─────────────┘
    │                   │                       │                        │
    │                   │                       │         10. Actualizar RefreshToken
    │                   │                       │         ├──────────────┐
    │                   │                       │         │UpdateUser    │
    │                   │                       │         │<─────────────┘
    │                   │                       │                        │
    │                   │                       │         11. Construir Response
    │                   │                       │         ├──────────────┐
    │                   │                       │         │BuildResponse │
    │                   │                       │         │<─────────────┘
    │                   │                       │                        │
    │                   │                       │     AuthLoginResponse  │
    │                   │                       │<───────────────────────┤
    │                   │                       │                        │
    │                   │          Response     │                        │
    │                   │<──────────────────────┤                        │
    │                   │                       │                        │
    │   Response JSON   │                       │                        │
    │<──────────────────┤                       │                        │
    │                   │                       │                        │
```

### Sub-Use Cases Involucrados

#### 1. Auth Validate User Use Case
**Propósito**: Validar credenciales del usuario

```python
class AuthValidateUserUseCase:
    async def execute(
        self, config: Config, params: AuthLoginRequest
    ) -> Union[User, str, None]:
        # 1. Buscar usuario por email
        # 2. Verificar contraseña con bcrypt
        # 3. Validar estado del usuario
        # 4. Retornar usuario o error
```

**Validaciones:**
- Usuario existe en la base de datos
- Password coincide con hash almacenado
- Usuario está activo (`state = true`)
- Usuario no está bloqueado

#### 2. Companies By User Use Case
**Propósito**: Obtener empresas asociadas al usuario

```python
class CompaniesByUserUseCase:
    async def execute(
        self, config: Config, params: CompaniesByUser
    ) -> Union[List[Company], str]:
        # 1. Buscar en user_location_rol por user_id
        # 2. Obtener company_ids únicos
        # 3. Cargar información completa de empresas
        # 4. Retornar lista de empresas
```

#### 3. Auth Initial User Data Use Case
**Propósito**: Cargar configuración inicial del usuario

```python
class AuthInitialUserDataUseCase:
    async def execute(
        self, config: Config, params: AuthInitialUserData
    ) -> Union[Tuple[Platform, User, Language, Location, Currency, Country, Company], str]:
        # 1. Obtener usuario por email
        # 2. Obtener platform_id del usuario
        # 3. Cargar Platform entity
        # 4. Cargar Language entity (del platform o del parámetro)
        # 5. Obtener primera location del usuario
        # 6. Obtener currency de la location
        # 7. Obtener country de la location
        # 8. Obtener company de la location
        # 9. Retornar tupla con todas las entidades
```

#### 4. Auth User Role And Permissions Use Case
**Propósito**: Obtener rol y permisos del usuario en la ubicación

```python
class AuthUserRoleAndPermissionsUseCase:
    async def execute(
        self, config: Config, params: AuthUserRoleAndPermissions
    ) -> Union[Tuple[List[Permission], Rol], str]:
        # 1. Buscar en user_location_rol (user + location)
        # 2. Obtener rol_id
        # 3. Buscar permisos en rol_permission
        # 4. Cargar entidades de permisos
        # 5. Retornar tupla (permisos, rol)
```

#### 5. Auth Menu Use Case
**Propósito**: Construir menú según permisos del usuario

```python
class AuthMenuUseCase:
    async def execute(
        self, config: Config, params: AuthMenu
    ) -> Union[List[MenuResponse], str]:
        # 1. Obtener permission_ids del usuario
        # 2. Buscar en menu_permission los menús asociados
        # 3. Filtrar por company_id
        # 4. Ordenar por orden
        # 5. Construir estructura jerárquica (si aplica)
        # 6. Retornar lista de menús
```

#### 6. Auth Currencies Use Case
**Propósito**: Obtener monedas de la ubicación

```python
class AuthCurrenciesUseCase:
    async def execute(
        self, config: Config, params: AuthCurremciesByLocation
    ) -> Union[List[Currency], str]:
        # 1. Buscar en currency_location por location_id
        # 2. Obtener currency_ids
        # 3. Cargar entidades de monedas
        # 4. Retornar lista de monedas
```

#### 7. Auth Locations Use Case
**Propósito**: Obtener ubicaciones del usuario en la empresa

```python
class AuthLocationsUseCase:
    async def execute(
        self, config: Config, params: AuthLocations
    ) -> Union[List[Location], str]:
        # 1. Buscar en user_location_rol (user_id + company_id)
        # 2. Obtener location_ids únicos
        # 3. Cargar entidades de ubicaciones
        # 4. Retornar lista de ubicaciones
```

#### 8. Auth Languages Use Case
**Propósito**: Obtener idiomas disponibles en el sistema

```python
class AuthLanguagesUseCase:
    async def execute(self, config: Config) -> Union[List[Language], str]:
        # 1. Listar todos los idiomas activos
        # 2. Retornar lista de idiomas
```

### Generación de Tokens

#### Access Token (JWT)

**Payload:**
```json
{
  "rol_id": "uuid",
  "rol_code": "ADMIN",
  "user_id": "uuid",
  "location_id": "uuid",
  "currency_id": "uuid",
  "company_id": "uuid",
  "permissions": ["save", "update", "delete", "read", "list"],
  "exp": 1699999999,  // Timestamp de expiración
  "iat": 1699996399   // Timestamp de emisión
}
```

**Configuración:**
- **Algoritmo**: HS256 (HMAC with SHA-256)
- **Secret Key**: `settings.jwt_secret_key`
- **Expiración**: `platform.token_expiration_minutes` (default: 60 minutos)

#### Refresh Token (JWT)

Similar al access token pero con expiración más larga:
- **Expiración**: `platform.refresh_token_expiration_minutes` (default: 1440 minutos / 24 horas)
- **Almacenamiento**: Se guarda en el campo `refresh_token` del usuario en BD

---

## Refresh Token

### Endpoint

```
POST /auth/refresh_token
```

### Request

**Headers:**
```
Authorization: Bearer <access_token>
Language: es | en
```

**Body:** (vacío)

### Flujo

1. Valida access token del header (puede estar expirado)
2. Extrae user_id del token
3. Busca usuario en BD
4. Valida refresh_token almacenado en BD
5. Si es válido, genera nuevo access token
6. Retorna nuevo access token (no modifica refresh token)

### Response

```json
{
  "message_type": "temporary",
  "notification_type": "success",
  "message": "Token renovado exitosamente",
  "response": {
    "token": "nuevo_jwt_token"
  }
}
```

---

## Logout

### Endpoint

```
POST /auth/logout
```

### Request

**Headers:**
```
Authorization: Bearer <access_token>
Language: es | en
```

**Body:** (vacío)

### Flujo

1. Valida access token del header
2. Extrae user_id del token
3. Actualiza usuario en BD: `refresh_token = null`
4. Invalida sesión (refresh token ya no es válido)

### Response

```json
{
  "message_type": "temporary",
  "notification_type": "success",
  "message": "Sesión cerrada exitosamente",
  "response": {
    "message": "Logout exitoso"
  }
}
```

---

## Create API Token

### Endpoint

```
POST /auth/create-api-token
```

### Request

**Headers:**
```
Authorization: Bearer <access_token>
Language: es | en
```

**Body:**
```json
{
  "name": "Integration API Token",
  "description": "Token para integración con sistema externo",
  "expiration_days": 365
}
```

### Flujo

1. Valida permisos del usuario (`PERMISSION_TYPE.SAVE`)
2. Genera token único (UUID o JWT especial)
3. Almacena en tabla `api_token`
4. Retorna token generado

### Response

```json
{
  "message_type": "temporary",
  "notification_type": "success",
  "message": "Token de API creado exitosamente",
  "response": {
    "id": "uuid",
    "name": "Integration API Token",
    "token": "generated_api_token",
    "created_date": "2024-11-08T10:00:00Z",
    "expiration_date": "2025-11-08T10:00:00Z"
  }
}
```

---

## Seguridad

### Hash de Contraseñas

- **Algoritmo**: Bcrypt
- **Salt**: Generado automáticamente por bcrypt
- **Rounds**: Default (10)

```python
# Hasheo
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Verificación
valid = bcrypt.checkpw(plain_password.encode('utf-8'), hashed)
```

### Tokens JWT

- **Firmado**: Sí (con secret key)
- **Encriptado**: No (payload es visible en base64)
- **Validación**: En cada request con `@check_permissions`

### Rate Limiting

Se puede aplicar rate limiting específico para endpoints de auth:

```python
# En middleware
login_limits = ["20/hour"]  # Máximo 20 intentos por hora
```

### Protección contra Ataques

- **Brute Force**: Rate limiting en `/auth/login`
- **Token Replay**: Validación de expiración
- **Session Hijacking**: Refresh token único por usuario
- **SQL Injection**: Uso de SQLAlchemy con parámetros preparados

---

## Referencias

- **[03-00] Business Flow Overview**: Documentación general del flujo de negocio
- **[04-06] Utilities - Token**: Implementación de generación de JWT
- **[04-06] Utilities - Password**: Implementación de hash de contraseñas
- **[07-03] Security Practices**: Mejores prácticas de seguridad

---

## Historial de Cambios

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0 | Nov 2024 | Creación inicial de especificación de Auth | Equipo de Desarrollo Goluti |

---

**Fin del Documento**


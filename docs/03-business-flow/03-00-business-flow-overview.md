# Flujo de Lógica de Negocio (Business Flow) - Overview

**Versión**: 1.0  
**Fecha**: Noviembre 2024  
**Estado**: Vigente  
**Autor(es)**: Equipo de Desarrollo Goluti

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [¿Qué es el Business Flow?](#qué-es-el-business-flow)
3. [Diferencias con Entity Flow](#diferencias-con-entity-flow)
4. [Flujo de Datos](#flujo-de-datos)
5. [Componentes del Flujo](#componentes-del-flujo)
6. [Casos de Uso Disponibles](#casos-de-uso-disponibles)
7. [Patrones y Convenciones](#patrones-y-convenciones)
   - 7.1. [Composición de Use Cases](#1-composición-de-use-cases)
   - 7.2. [Manejo de Errores en Cadena](#2-manejo-de-errores-en-cadena)
   - 7.3. [Modelos Request/Response Específicos](#3-modelos-requestresponse-específicos)
   - 7.4. [Mappers Especializados](#4-mappers-especializados)
   - 7.5. [Decoradores](#5-decoradores)
   - 7.6. [Organización de Use Cases en Business](#6-organización-de-use-cases-en-business)
8. [Ejemplo: Auth Login](#ejemplo-auth-login)
9. [Referencias](#referencias)

---

## Introducción

El **Business Flow** (Flujo de Lógica de Negocio) es el segundo flujo principal del Goluti Backend Platform. A diferencia del Entity Flow que maneja operaciones CRUD estándar, el Business Flow implementa **lógica de negocio compleja** que involucra múltiples entidades, validaciones especializadas, orquestación de servicios y procesos de negocio específicos.

### Objetivo

Proporcionar una estructura para:
- Implementar procesos de negocio complejos
- Orquestar múltiples casos de uso de entidades
- Ejecutar validaciones y transformaciones especializadas
- Componer respuestas complejas con datos de múltiples fuentes
- Mantener la separación de responsabilidades

---

## ¿Qué es el Business Flow?

El Business Flow es un patrón arquitectónico para **operaciones que no son CRUD simple**. Estas operaciones:

- **Involucran múltiples entidades**: Leen/escriben en varias tablas
- **Tienen lógica compleja**: Validaciones especiales, cálculos, transformaciones
- **Orquestan múltiples pasos**: Ejecutan una secuencia de operaciones
- **Responden con modelos complejos**: Estructuras de datos especializadas
- **Pueden tener efectos secundarios**: Generación de tokens, envío de emails, etc.

### Ejemplos de Business Logic

- **Autenticación (Login)**: Valida credenciales, carga configuración, genera tokens
- **Refresh Token**: Valida refresh token, genera nuevo access token
- **Logout**: Invalida refresh token del usuario
- **Create API Token**: Genera token de API con permisos específicos
- **Onboarding de Usuario**: Crea usuario, asigna rol, configura permisos, envía email
- **Reportes Complejos**: Agrega datos de múltiples entidades

---

## Diferencias con Entity Flow

| Aspecto | Entity Flow | Business Flow |
|---------|-------------|---------------|
| **Operaciones** | CRUD estándar (Save, Update, List, Read, Delete) | Operaciones personalizadas |
| **Modelos** | 5 modelos por entidad (Save, Update, Read, Delete, List) | Modelos Request/Response específicos |
| **Complejidad** | Simple, una entidad a la vez | Complejo, múltiples entidades |
| **Use Cases** | Un use case por operación | Use cases compuestos y especializados |
| **Endpoints** | Predecibles (`POST /{entity}`, `GET /{entity}/{id}`) | Específicos al caso de uso (`POST /auth/login`) |
| **Lógica** | Validación básica, persistencia directa | Validaciones complejas, orquestación |
| **Repositorios** | Uso directo de repositorios de entidad | Puede usar múltiples repositorios + use cases |

---

## Flujo de Datos

### Diagrama de Flujo Business

```
┌──────────────┐
│   Cliente    │
│   (HTTP)     │
└──────┬───────┘
       │ 1. HTTP Request (POST/GET)
       │    Headers: Authorization, Language
       │    Body: BusinessRequest (JSON)
       ▼
┌──────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                     │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Business Router (FastAPI)                          │  │
│  │  - Valida BusinessRequest (Pydantic)                │  │
│  │  - Extrae configuración                             │  │
│  │  - Aplica decoradores (permisos si aplica)          │  │
│  │  - Invoca Business Controller                       │  │
│  └────────────────────────────────────────────────────┘  │
└───────────────────────┬──────────────────────────────────┘
                        │ 2. Config + BusinessRequest
                        ▼
┌──────────────────────────────────────────────────────────┐
│               INFRASTRUCTURE WEB LAYER                    │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Business Controller                                │  │
│  │  - Invoca Business Use Case principal               │  │
│  │  - Maneja resultado complejo                        │  │
│  │  - Construye Response con BusinessResponse          │  │
│  └────────────────────────────────────────────────────┘  │
└───────────────────────┬──────────────────────────────────┘
                        │ 3. Config + BusinessRequest
                        ▼
┌──────────────────────────────────────────────────────────┐
│                      DOMAIN LAYER                         │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Business Use Case (Orquestador)                    │  │
│  │  ┌──────────────────────────────────────────────┐  │  │
│  │  │ 1. Validaciones iniciales                     │  │  │
│  │  │ 2. Invoca Use Case A (Entity)                 │  │  │
│  │  │ 3. Invoca Use Case B (Entity)                 │  │  │
│  │  │ 4. Invoca Use Case C (Business)               │  │  │
│  │  │ 5. Aplica lógica de transformación            │  │  │
│  │  │ 6. Genera respuesta compleja                  │  │  │
│  │  │ 7. Efectos secundarios (tokens, emails, etc.) │  │  │
│  │  └──────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────┘  │
└───────────────────────┬──────────────────────────────────┘
                        │ 4. Usa múltiples Use Cases y Repositories
                        ▼
                 (Interacción con múltiples fuentes)
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│                    HTTP Response                          │
│  {                                                        │
│    "message_type": "temporary",                           │
│    "notification_type": "success",                        │
│    "message": "Operación exitosa",                        │
│    "response": {                                          │
│      /* BusinessResponse complejo */                      │
│      "platform_configuration": { ... },                   │
│      "platform_variations": { ... },                      │
│      "token": "..."                                       │
│    }                                                      │
│  }                                                        │
└──────────────────────────────────────────────────────────┘
```

---

## Componentes del Flujo

### 1. **Business Models** (`src/domain/models/business/{module}/`)

Modelos Pydantic específicos para el caso de uso de negocio:

**Estructura típica:**
```
src/domain/models/business/auth/
├── login/
│   ├── auth_login_request.py          # Request del endpoint
│   ├── auth_login_response.py         # Response principal
│   ├── auth_initial_user_data.py      # Modelos internos
│   ├── auth_locations.py              # Modelos internos
│   ├── auth_currencies_by_location.py
│   ├── auth_user_role_and_permissions.py
│   ├── companies_by_user.py
│   ├── auth_menu.py
│   └── index.py                       # Exportaciones
```

**Ejemplo: Login Request**
```python
class AuthLoginRequest(BaseModel):
    email: EmailStr
    password: str
    company_id: Optional[UUID4] = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123"
            }
        }
```

**Ejemplo: Login Response (Complejo)**
```python
class AuthLoginResponse(BaseModel):
    platform_configuration: PlatformConfiguration  # Configuración inicial
    platform_variations: PlatformVariations        # Opciones disponibles
    token: str                                     # Access token JWT

class PlatformConfiguration(BaseModel):
    user: UserLoginResponse
    currency: CurrencyLoginResponse
    location: LocationLoginResponse
    language: LanguageLoginResponse
    platform: PlatformLoginResponse
    country: CountryLoginResponse
    company: CompanyLoginResponse
    rol: RolLoginResponse
    permissions: List[Permission]
    menu: List[MenuResponse]

class PlatformVariations(BaseModel):
    currencies: List[Currency]
    locations: List[Location]
    languages: List[Language]
    companies: List[Company]
```

### 2. **Business Use Cases** (`src/domain/services/use_cases/business/{module}/`)

Casos de uso que orquestan la lógica de negocio compleja:

**Estructura:**
```
src/domain/services/use_cases/business/auth/
├── login/
│   ├── auth_login_use_case.py                    # Use case principal
│   ├── auth_validate_user_use_case.py            # Sub-use case
│   ├── auth_initial_user_data_use_case.py
│   ├── auth_locations_use_case.py
│   ├── auth_currencies_use_case.py
│   ├── auth_languages_use_case.py
│   ├── auth_menu_use_case.py
│   ├── auth_user_role_and_permissions.py
│   └── companies_by_user_use_case.py
```

**Ejemplo: Auth Login Use Case (Orquestador)**
```python
class AuthLoginUseCase:
    def __init__(self):
        self.auth_validate_user_use_case = AuthValidateUserUseCase()
        self.user_update_use_case = UserUpdateUseCase(user_repository)
        self.auth_languages_use_case = AuthLanguagesUseCase()
        self.auth_locations_use_case = AuthLocationsUseCase()
        self.auth_currencies_use_case = AuthCurrenciesUseCase()
        self.auth_initial_user_data_use_case = AuthInitialUserDataUseCase()
        self.auth_menu_use_case = AuthMenuUseCase()
        self.auth_user_role_and_permissions_use_case = AuthUserRoleAndPermissionsUseCase()
        self.companies_by_user_use_case = CompaniesByUserUseCase()
        self.message = Message()
        self.token = Token()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self, config: Config, params: AuthLoginRequest
    ) -> Union[AuthLoginResponse, str, None]:
        # 1. Validar credenciales del usuario
        user_validator = await self.auth_validate_user_use_case.execute(
            config=config, params=params
        )
        if isinstance(user_validator, str):
            return user_validator

        # 2. Obtener empresas del usuario
        companies_by_user = await self.companies_by_user_use_case.execute(
            config=config, params=CompaniesByUser(email=params.email)
        )
        if isinstance(companies_by_user, str):
            return companies_by_user

        # 3. Cargar datos iniciales (platform, user, language, etc.)
        initial_user_data = await self.auth_initial_user_data_use_case.execute(
            config=config, params=AuthInitialUserData(email=params.email)
        )
        if isinstance(initial_user_data, str):
            return initial_user_data

        (platform_entity, user_entity, language_entity, 
         location_entity, currency_entity, country_entity, 
         company_entity) = initial_user_data

        # 4. Obtener rol y permisos del usuario
        user_role_and_permissions = await self.auth_user_role_and_permissions_use_case.execute(
            config=config,
            params=AuthUserRoleAndPermissions(
                email=params.email, location=location_entity.id
            ),
        )
        if isinstance(user_role_and_permissions, str):
            return user_role_and_permissions

        permissions, rol_q = user_role_and_permissions

        # 5. Construir menú según permisos
        auth_menu = await self.auth_menu_use_case.execute(
            config=config,
            params=AuthMenu(company=company_entity.id, permissions=permissions),
        )
        if isinstance(auth_menu, str):
            return auth_menu

        # 6. Obtener monedas de la ubicación
        currencies = await self.auth_currencies_use_case.execute(
            config=config, 
            params=AuthCurremciesByLocation(location=location_entity.id)
        )
        if isinstance(currencies, str):
            return currencies

        # 7. Obtener ubicaciones del usuario
        locations = await self.auth_locations_use_case.execute(
            config=config,
            params=AuthLocations(user_id=user_entity.id, company_id=company_entity.id),
        )
        if isinstance(locations, str):
            return locations

        # 8. Obtener idiomas disponibles
        languages = await self.auth_languages_use_case.execute(config=config)
        if isinstance(languages, str):
            return languages

        # 9. Generar tokens JWT
        access_token = AccessToken(
            rol_id=str(rol_q.id),
            rol_code=str(rol_q.code),
            user_id=str(user_entity.id),
            location_id=str(location_entity.id),
            currency_id=str(currency_entity.id),
            company_id=str(company_entity.id),
            token_expiration_minutes=platform_entity.token_expiration_minutes,
            permissions=[permission.name for permission in permissions],
        )

        token = self.token.create_access_token(data=access_token)
        refresh_token = self.token.create_refresh_token(data=access_token)

        # 10. Actualizar refresh token del usuario
        user_update = await self.user_update_use_case.execute(
            config=config,
            params=UserUpdate(
                id=user_entity.id,
                # ... otros campos ...
                refresh_token=refresh_token,
            ),
        )
        if isinstance(user_update, str):
            return user_update

        # 11. Construir respuesta compleja
        result = AuthLoginResponse(
            platform_configuration=PlatformConfiguration(
                user=map_to_user_login_response(user_entity),
                currency=map_to_currecy_login_response(currency_entity),
                location=map_to_location_login_response(location_entity),
                language=map_to_language_login_response(language_entity),
                platform=map_to_platform_login_response(platform_entity),
                country=map_to_country_login_response(country_entity),
                company=map_to_company_login_response(company_entity),
                rol=map_to_rol_login_response(rol_q),
                permissions=permissions,
                menu=auth_menu,
            ),
            platform_variations=PlatformVariations(
                currencies=currencies,
                locations=locations,
                languages=languages,
                companies=companies_by_user,
            ),
            token=token,
        )

        return result
```

### 3. **Business Controllers** (`src/infrastructure/web/controller/business/`)

Controladores que manejan la invocación de use cases de negocio:

```python
class AuthController:
    def __init__(self) -> None:
        self.auth_login_use_case = AuthLoginUseCase()
        self.auth_refresh_token_use_case = AuthRefreshTokenUseCase()
        self.auth_logout_use_case = AuthLogoutUseCase()
        self.auth_create_api_token_use_case = AuthCreateApiTokenUseCase()
        self.message = Message()

    @execute_transaction(layer=LAYER.I_W_C_B.value, enabled=settings.has_track)
    async def login(
        self, config: Config, params: AuthLoginRequest
    ) -> Response[AuthLoginResponse]:
        result = await self.auth_login_use_case.execute(config, params)
        
        if isinstance(result, str):
            return Response.error(None, result)
        
        return Response.success_temporary_message(
            response=result,
            message=await self.message.get_message(...)
        )

    # ... otros métodos (refresh_token, logout, create_api_token)
```

### 4. **Business Routers** (`src/infrastructure/web/business_routes/`)

Endpoints HTTP específicos para operaciones de negocio:

```python
auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}}
)

auth_controller = AuthController()

@auth_router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=Response[AuthLoginResponse]
)
@execute_transaction_route(enabled=settings.has_track)
async def login(
    params: AuthLoginRequest,
    config: Config = Depends(get_config_login)
) -> Response[AuthLoginResponse]:
    return await auth_controller.login(config=config, params=params)

@auth_router.post(
    "/refresh_token",
    status_code=status.HTTP_200_OK,
    response_model=Response[AuthRefreshTokenResponse],
)
@check_permissions([PERMISSION_TYPE.UPDATE.value])
@execute_transaction_route(enabled=settings.has_track)
async def refresh_token(
    config: Config = Depends(get_config),
) -> Response[AuthRefreshTokenResponse]:
    return await auth_controller.refresh_token(config=config)

@auth_router.post("/logout", ...)
async def logout(...) -> Response[AuthLogoutResponse]:
    # ...

@auth_router.post("/create-api-token", ...)
async def create_api_token(...) -> Response[CreateApiTokenResponse]:
    # ...
```

---

## Casos de Uso Disponibles

### Módulo: Auth (Autenticación)

| Operación | Endpoint | Descripción |
|-----------|----------|-------------|
| **Login** | `POST /auth/login` | Autenticación de usuario, generación de tokens |
| **Refresh Token** | `POST /auth/refresh_token` | Renovación de access token |
| **Logout** | `POST /auth/logout` | Cierre de sesión, invalidación de refresh token |
| **Create API Token** | `POST /auth/create-api-token` | Generación de token de API para integraciones |

---

## Patrones y Convenciones

### 1. Composición de Use Cases

Los Business Use Cases **componen** otros use cases (Entity o Business):

```python
class ComplexBusinessUseCase:
    def __init__(self):
        # Reutilizar use cases de entidades
        self.user_repository = UserRepository()
        self.company_list_use_case = CompanyListUseCase(...)
        self.permission_list_use_case = PermissionListUseCase(...)
        
        # Reutilizar otros business use cases
        self.validate_something_use_case = ValidateSomethingUseCase()
```

### 2. Manejo de Errores en Cadena

Cada sub-operación puede fallar, se verifica en cada paso:

```python
result1 = await self.use_case_1.execute(...)
if isinstance(result1, str):  # Error
    return result1  # Propagar error

result2 = await self.use_case_2.execute(...)
if isinstance(result2, str):
    return result2

# Continuar solo si todo es exitoso
```

### 3. Modelos Request/Response Específicos

No se reutilizan modelos de Entity, se crean modelos específicos:

```python
# ❌ No hacer
class LoginRequest(UserSave):  # No heredar de entity models
    pass

# ✅ Hacer
class AuthLoginRequest(BaseModel):  # Modelo específico
    email: EmailStr
    password: str
    company_id: Optional[UUID4] = None
```

### 4. Mappers Especializados

Se crean mappers específicos para transformar entidades en respuestas de negocio:

```python
# src/infrastructure/database/repositories/business/mappers/auth/login/login_mapper.py

def map_to_user_login_response(user_entity: User) -> UserLoginResponse:
    """Mapea User a una respuesta específica de login"""
    return UserLoginResponse(
        id=user_entity.id,
        email=user_entity.email,
        first_name=user_entity.first_name,
        last_name=user_entity.last_name,
        # Solo campos necesarios para login
    )
```

### 5. Decoradores

- `@execute_transaction`: Tracking de transacciones
- `@check_permissions`: Solo si la operación requiere autenticación

Nota: Login no requiere `@check_permissions` porque es el punto de entrada.

### 6. Organización de Use Cases en Business

**Regla**: Cada flujo de negocio debe tener **su propia carpeta** dentro de `auth/` (o el contexto correspondiente). Dentro de esa carpeta van **todos** los casos de uso relacionados con ese flujo.

#### Estructura Correcta ✅

```
src/domain/services/use_cases/business/auth/
├── create_company/
│   ├── create_company_use_case.py (principal)
│   ├── clone_menus_for_company_use_case.py (auxiliar)
│   ├── clone_menu_permissions_for_company_use_case.py (auxiliar)
│   └── __init__.py
├── create_user_internal/
│   ├── create_user_internal_use_case.py (principal)
│   ├── validate_user_internal_use_case.py (auxiliar)
│   └── __init__.py
├── create_user_external/
│   ├── create_user_external_use_case.py (principal)
│   └── __init__.py
├── login/
│   ├── auth_login_use_case.py (principal)
│   ├── auth_validate_user_use_case.py (auxiliar)
│   ├── auth_menu_use_case.py (auxiliar)
│   └── __init__.py
├── logout/
│   ├── auth_logout_use_case.py
│   └── __init__.py
└── __init__.py
```

#### Beneficios de Esta Organización

1. ✅ **Agrupación lógica**: Todos los casos de uso de un flujo están juntos
2. ✅ **Facilita navegación**: Es fácil encontrar todo lo relacionado con un flujo
3. ✅ **Escalabilidad**: Cada flujo puede crecer independientemente
4. ✅ **Claridad**: Se ve inmediatamente qué casos de uso son auxiliares de cuál principal
5. ✅ **Modularidad**: Cada carpeta es una unidad funcional completa

#### Nomenclatura

- **Carpeta**: Nombre del flujo en snake_case
  - Ejemplo: `create_company/`, `login/`, `refresh_token/`
- **Archivo principal**: `{nombre_flujo}_use_case.py`
  - Ejemplo: `create_company_use_case.py`, `auth_login_use_case.py`
- **Archivos auxiliares**: `{operacion}_use_case.py` o `{operacion}_for_{contexto}_use_case.py`
  - Ejemplo: `clone_menus_for_company_use_case.py`
  - Ejemplo: `validate_user_internal_use_case.py`

#### Imports

```python
# ✅ Correcto
from src.domain.services.use_cases.business.auth.create_company.create_company_use_case import CreateCompanyUseCase
from src.domain.services.use_cases.business.auth.create_company.clone_menus_for_company_use_case import CloneMenusForCompanyUseCase

# Los casos de uso auxiliares se importan desde la misma carpeta del flujo
# create_company_use_case.py
from .clone_menus_for_company_use_case import CloneMenusForCompanyUseCase
from .clone_menu_permissions_for_company_use_case import CloneMenuPermissionsForCompanyUseCase
```

#### Casos de Uso Auxiliares

Los casos de uso auxiliares van en la **misma carpeta** que el caso de uso principal que los utiliza:

```python
# src/domain/services/use_cases/business/auth/create_company/create_company_use_case.py
from .clone_menus_for_company_use_case import CloneMenusForCompanyUseCase
from .clone_menu_permissions_for_company_use_case import CloneMenuPermissionsForCompanyUseCase

class CreateCompanyUseCase:
    def __init__(self):
        self.clone_menus_uc = CloneMenusForCompanyUseCase()
        self.clone_permissions_uc = CloneMenuPermissionsForCompanyUseCase()
```

---

## Ejemplo: Auth Login

Ver documento **[03-05-auth-flow-specification.md]** para la especificación completa del flujo de autenticación con:
- Diagrama de secuencia detallado
- Todos los sub-use cases involucrados
- Validaciones ejecutadas
- Estructura completa de la respuesta
- Ejemplos de peticiones y respuestas

---

## Referencias

- **[03-01] Business Models**: Especificación de modelos de negocio
- **[03-02] Business Use Cases**: Especificación de casos de uso de negocio
- **[03-03] Business Controllers**: Especificación de controladores de negocio
- **[03-04] Business Routers**: Especificación de routers de negocio
- **[03-05] Auth Flow Specification**: Especificación completa del flujo de autenticación
- **[03-06] Business Flow Examples**: Ejemplos prácticos completos

---

## Historial de Cambios

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0 | Nov 2024 | Creación inicial del documento de Business Flow | Equipo de Desarrollo Goluti |
| 1.1 | Nov 12, 2024 | Agregada sección 7.6 "Organización de Use Cases en Business": Cada flujo de negocio tiene su propia carpeta dentro de auth/ con todos sus casos de uso (principal + auxiliares). Incluye ejemplos de estructura, nomenclatura e imports. | Equipo de Desarrollo Goluti |

---

**Fin del Documento**


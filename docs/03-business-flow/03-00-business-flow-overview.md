# Especificación de Business Flow - Cómo Construir Flujos de Negocio

**Versión**: 2.0  
**Fecha**: Enero 23, 2026  
**Estado**: Vigente  
**Autor(es)**: Equipo de Desarrollo Goluti

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [¿Qué es el Business Flow?](#qué-es-el-business-flow)
3. [Diferencias con Entity Flow](#diferencias-con-entity-flow)
4. [Flujo de Datos](#flujo-de-datos)
5. [Componentes del Flujo](#componentes-del-flujo)
6. [Patrones y Convenciones](#patrones-y-convenciones)
   - 6.1. [Composición de Use Cases](#1-composición-de-use-cases)
   - 6.2. [Manejo de Errores en Cadena](#2-manejo-de-errores-en-cadena)
   - 6.3. [Modelos Request/Response Específicos](#3-modelos-requestresponse-específicos)
   - 6.4. [Mappers Especializados](#4-mappers-especializados)
   - 6.5. [Decoradores](#5-decoradores)
   - 6.6. [Organización de Use Cases en Business](#6-organización-de-use-cases-en-business)
   - 6.7. [Tipos Genéricos en Response](#7-tipos-genéricos-en-response)
   - 6.8. [Documentación de Swagger](#8-documentación-de-swagger)
7. [Guía: Crear un Nuevo Módulo de Negocio](#guía-crear-un-nuevo-módulo-de-negocio)
8. [Referencias](#referencias)

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

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
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

**Regla**: Cada flujo de negocio debe tener **su propia carpeta** dentro del módulo correspondiente (`auth/`, `geography/`, etc.). Dentro de esa carpeta van **todos** los casos de uso relacionados con ese flujo, permitiendo que crezca con sub-use-cases si los necesita.

#### Estructura por Módulo

Cada **módulo de negocio** tiene su propia carpeta bajo `use_cases/business/`. Dentro, cada **flujo** tiene su subcarpeta:

```
src/domain/services/use_cases/business/
├── auth/                              # Módulo: Autenticación
│   ├── login/                         # Flujo: Login
│   │   ├── auth_login_use_case.py     #   Principal
│   │   ├── auth_validate_user_use_case.py  #   Auxiliar
│   │   ├── auth_menu_use_case.py      #   Auxiliar
│   │   └── __init__.py
│   ├── create_company/                # Flujo: Crear empresa
│   │   ├── create_company_use_case.py #   Principal
│   │   ├── clone_menus_for_company_use_case.py  #   Auxiliar
│   │   ├── clone_menu_permissions_for_company_use_case.py
│   │   └── __init__.py
│   ├── create_user_external/
│   │   ├── create_user_external_use_case.py
│   │   └── __init__.py
│   ├── logout/
│   │   ├── auth_logout_use_case.py
│   │   └── __init__.py
│   └── __init__.py
│
├── geography/                         # Módulo: Geografía
│   ├── countries/                     # Flujo: Listar países
│   │   ├── countries_use_case.py      #   Principal
│   │   └── __init__.py
│   ├── types_by_country/              # Flujo: Tipos por país
│   │   ├── types_by_country_use_case.py
│   │   └── __init__.py
│   ├── hierarchy/                     # Flujo: Jerarquía
│   │   ├── hierarchy_use_case.py
│   │   └── __init__.py
│   ├── children/
│   │   ├── children_use_case.py
│   │   └── __init__.py
│   └── __init__.py
```

#### Beneficios de Esta Organización

1. **Agrupación lógica**: Todos los casos de uso de un flujo están juntos
2. **Facilita navegación**: Es fácil encontrar todo lo relacionado con un flujo
3. **Escalabilidad**: Cada flujo puede crecer independientemente con sub-use-cases
4. **Claridad**: Se ve inmediatamente qué casos de uso son auxiliares de cuál principal
5. **Modularidad**: Cada carpeta es una unidad funcional completa

#### Nomenclatura: Evitar Prefijos Redundantes

La carpeta del módulo ya provee el contexto. **No repetir el nombre del módulo** en archivos ni clases dentro de esa carpeta:

```
# ❌ INCORRECTO - Prefijo redundante
geography/
├── countries/
│   └── geography_countries_use_case.py    → GeographyCountriesUseCase

# ✅ CORRECTO - Sin prefijo redundante
geography/
├── countries/
│   └── countries_use_case.py              → CountriesUseCase
├── hierarchy/
│   └── hierarchy_use_case.py              → HierarchyUseCase
├── detail/
│   └── detail_use_case.py                 → DetailUseCase
```

> **Nota**: El módulo `auth` es una excepción histórica donde algunos archivos conservan el prefijo `auth_` por claridad semántica (ej: `auth_login_use_case.py`). Para módulos **nuevos**, seguir la convención sin prefijo redundante.

#### Nomenclatura General

- **Carpeta del módulo**: Nombre del módulo en snake_case → `auth/`, `geography/`
- **Carpeta del flujo**: Nombre del flujo en snake_case → `login/`, `countries/`, `hierarchy/`
- **Archivo principal**: `{nombre_flujo}_use_case.py` → `countries_use_case.py`
- **Clase principal**: `{NombreFlujo}UseCase` → `CountriesUseCase`
- **Archivos auxiliares**: `{operacion}_use_case.py` → `validate_country_use_case.py`

#### Imports

```python
# ✅ Import desde el controller (path completo)
from src.domain.services.use_cases.business.geography.countries.countries_use_case import CountriesUseCase
from src.domain.services.use_cases.business.geography.hierarchy.hierarchy_use_case import HierarchyUseCase

# ✅ Import relativo entre use cases auxiliares (misma carpeta)
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

#### Stack Completo por Módulo de Negocio

Cada módulo de negocio sigue este stack completo. El nombre del módulo se usa como **namespace** en cada capa:

| Capa | Ruta | Ejemplo (geography) |
|------|------|---------------------|
| **Router** | `business_routes/{modulo}_router.py` | `geography_router.py` → `geography_router` |
| **Controller** | `controller/business/{modulo}_controller.py` | `geography_controller.py` → `GeographyController` |
| **Use Cases** | `use_cases/business/{modulo}/{flujo}/{flujo}_use_case.py` | `geography/countries/countries_use_case.py` → `CountriesUseCase` |
| **Repository** | `repositories/business/{modulo}_repository.py` | `geography_repository.py` → `GeographyRepository` |
| **Mapper** | `repositories/business/mappers/{modulo}/{modulo}_mapper.py` | `geography/geography_mapper.py` |
| **Response Models** | `models/business/{modulo}/` | `geography/geo_division_item_response.py` |
| **Registro** | `routes/route_business.py` | `app.include_router(geography_router)` |

> **Importante**: El tag del router (`tags=["Geography"]`) debe ser **diferente** al tag de la entidad (`tags=["GeoDivision"]`) para que en Swagger/OpenAPI se muestren como grupos separados.

### 7. Tipos Genéricos en Response

**OBLIGATORIO**: Todos los endpoints de Business Flow deben especificar el tipo genérico de `Response[T]` en:
- `response_model` del decorador del router
- Firma de retorno de la función del router
- Firma de retorno del método del controller

```python
# ✅ CORRECTO - Tipo específico
@geography_router.post(
    "/country/types",
    response_model=Response[List[GeoDivisionTypeByCountryResponse]],  # ← Tipo específico
)
async def types_by_country(
    params: TypesByCountryRequest, 
    config: Config = Depends(get_config)
) -> Response[List[GeoDivisionTypeByCountryResponse]]:  # ← Tipo específico
    return await geography_controller.types_by_country(config, params)

# Controller
class GeographyController:
    async def types_by_country(
        self, config: Config, params: TypesByCountryRequest
    ) -> Response[List[GeoDivisionTypeByCountryResponse]]:  # ← Tipo específico
        result = await self.types_by_country_use_case.execute(config, params)
        if isinstance(result, str):
            return Response.error(None, result)
        return Response.success_temporary_message(response=result, message=...)

# ❌ INCORRECTO - Response genérico
@geography_router.post("/country/types", response_model=Response)  # ← Demasiado genérico
async def types_by_country(...) -> Response:  # ← Demasiado genérico
    ...
```

**Beneficios:**
- ✅ Swagger/OpenAPI genera documentación exacta del schema de respuesta
- ✅ Type safety completo en el stack
- ✅ Mejor autocompletado en IDEs
- ✅ Validación de tipos en tiempo de desarrollo

**Tipos comunes:**
- `Response[T]` - Respuesta única
- `Response[List[T]]` - Lista de elementos
- `Response[Dict[str, Any]]` - Diccionario dinámico (evitar si es posible)

### 8. Documentación de Swagger

**OBLIGATORIO**: Cada endpoint debe incluir `summary` y `description` para documentación en Swagger:

```python
@geography_router.post(
    "/country/types",
    status_code=status.HTTP_200_OK,
    response_model=Response[List[GeoDivisionTypeByCountryResponse]],
    summary="Tipos de división por país",  # ← Título corto
    description="""
    Obtiene todos los tipos de división geográfica disponibles para un país específico 
    junto con el conteo de registros por tipo.
    
    **Caso de uso:**
    - Mostrar estructura geográfica disponible de un país
    - Determinar qué niveles de división están implementados
    - Obtener estadísticas de divisiones por tipo
    
    **Respuesta incluye:**
    - ID del tipo de división
    - Nombre del tipo (DEPARTMENT, CITY, etc.)
    - Etiqueta localizada (Departamento, Ciudad, etc.)
    - Nivel jerárquico (1, 2, 3...)
    - Cantidad de divisiones de ese tipo
    
    **Ejemplo de request:**
    ```json
    {
      "country_id": "uuid-del-pais"
    }
    ```
    """,  # ← Descripción detallada con markdown
)
async def types_by_country(...):
    ...
```

**Elementos requeridos en `description`:**
1. **Qué hace**: Descripción clara de la operación
2. **Caso de uso**: Escenarios concretos de cuándo usar el endpoint
3. **Respuesta incluye**: Qué campos retorna y su significado
4. **Ejemplo de request**: JSON de ejemplo (si aplica)
5. **Notas especiales**: Limitaciones, consideraciones, diferencias con otros endpoints

**Formato:**
- Usar markdown para formato (negrita, listas, code blocks)
- Incluir ejemplos JSON cuando sea útil
- Ser conciso pero completo
- Usar sección `**Título:**` para organizar

---

## Guía: Crear un Nuevo Módulo de Negocio

Esta sección describe **paso a paso** cómo crear un nuevo módulo de Business Flow desde cero.

### Paso 1: Definir el Módulo y sus Flujos

**Decisión inicial:**
- ¿Qué módulo de negocio estás creando? (ej: `payments`, `notifications`, `reports`)
- ¿Qué operaciones/flujos necesitas? (ej: `process_payment`, `send_notification`)
- ¿Qué entidades involucra?
- ¿Requiere autenticación?

**Ejemplo:** Crearemos un módulo `geography` con operaciones para consultar divisiones geográficas.

### Paso 2: Crear Modelos Request/Response

**Ubicación:** `src/domain/models/business/{modulo}/`

```bash
mkdir -p src/domain/models/business/geography
```

**Crear archivos:**

```python
# types_by_country_request.py
from pydantic import BaseModel, Field
from uuid import UUID

class TypesByCountryRequest(BaseModel):
    country_id: UUID = Field(...)
```

```python
# geo_division_type_by_country_response.py
from pydantic import BaseModel, Field
from uuid import UUID

class GeoDivisionTypeByCountryResponse(BaseModel):
    id: UUID = Field(...)
    name: str = Field(...)
    label: str = Field(...)
    level: int = Field(...)
    count: int = Field(...)
```

**Crear index.py:**
```python
# index.py
from .types_by_country_request import TypesByCountryRequest
from .geo_division_type_by_country_response import GeoDivisionTypeByCountryResponse

__all__ = [
    "TypesByCountryRequest",
    "GeoDivisionTypeByCountryResponse",
]
```

**Consideraciones:**
- Usar `UUID` (no `UUID4`) si necesitas aceptar UUIDs fijos/predecibles
- Usar `Field(...)` para campos obligatorios
- Usar `Field(default=None)` para campos opcionales
- Agregar `json_schema_extra` con ejemplos si es útil

### Paso 3: Crear Repository (si necesitas queries especiales)

**Ubicación:** `src/infrastructure/database/repositories/business/{modulo}_repository.py`

```python
# geography_repository.py
from uuid import UUID
from typing import List, Optional
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.infrastructure.database.entities.geo_division_entity import GeoDivisionEntity

class GeographyRepository:

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def get_types_by_country(
        self, config: Config, country_id: UUID
    ) -> Optional[List]:
        async with config.async_db as db:
            from sqlalchemy import text as sa_text
            
            schema = settings.database_schema
            raw_sql = sa_text(f"""
                WITH RECURSIVE descendants AS (
                    SELECT id, geo_division_type_id, level
                    FROM {schema}.geo_division
                    WHERE top_id = :country_id AND state = TRUE
                    UNION ALL
                    SELECT gd.id, gd.geo_division_type_id, gd.level
                    FROM {schema}.geo_division gd
                    INNER JOIN descendants d ON gd.top_id = d.id
                    WHERE gd.state = TRUE
                )
                SELECT 
                    gdt.id, gdt.name, gdt.label, d.level, COUNT(d.id) as count
                FROM descendants d
                INNER JOIN {schema}.geo_division_type gdt 
                    ON d.geo_division_type_id = gdt.id
                WHERE gdt.state = TRUE
                GROUP BY gdt.id, gdt.name, gdt.label, d.level
                ORDER BY d.level
            """)
            
            result = await db.execute(raw_sql, {"country_id": str(country_id)})
            rows = result.all()
            return rows if rows else None
```

**Importante cuando uses SQL raw:**
- ✅ **SIEMPRE** especifica el schema: `{schema}.tabla`
- ✅ Usa `schema = settings.database_schema`
- ✅ Usa f-strings para interpolar el schema
- ❌ NO uses SQL raw sin schema: causará `relation does not exist`

### Paso 4: Crear Mappers (si necesitas transformaciones)

**Ubicación:** `src/infrastructure/database/repositories/business/mappers/{modulo}/{modulo}_mapper.py`

```python
# mappers/geography/geography_mapper.py
from src.domain.models.business.geography.index import GeoDivisionTypeByCountryResponse
from src.infrastructure.database.entities.geo_division_type_entity import GeoDivisionTypeEntity

def map_to_geo_division_type_by_country_response(
    type_entity: GeoDivisionTypeEntity, level: int, count: int
) -> GeoDivisionTypeByCountryResponse:
    return GeoDivisionTypeByCountryResponse(
        id=type_entity.id,
        name=type_entity.name,
        label=type_entity.label,
        level=level,
        count=count,
    )
```

### Paso 5: Crear Use Cases

**Ubicación:** `src/domain/services/use_cases/business/{modulo}/{flujo}/`

```bash
mkdir -p src/domain/services/use_cases/business/geography/types_by_country
```

```python
# types_by_country_use_case.py
from typing import List, Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.geography.index import (
    GeoDivisionTypeByCountryResponse,
    TypesByCountryRequest,
)
from src.infrastructure.database.repositories.business.geography_repository import (
    GeographyRepository,
)
from src.infrastructure.database.repositories.business.mappers.geography.geography_mapper import (
    map_to_geo_division_type_by_country_response,
)

class TypesByCountryUseCase:
    def __init__(self):
        self.geography_repository = GeographyRepository()
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self, config: Config, params: TypesByCountryRequest
    ) -> Union[List[GeoDivisionTypeByCountryResponse], str]:
        # 1. Obtener datos del repositorio
        rows = await self.geography_repository.get_types_by_country(
            config=config, country_id=params.country_id
        )
        
        # 2. Validar que se encontraron resultados
        if not rows:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_NO_RESULTS_FOUND.value
                ),
            )
        
        # 3. Mapear a Response models
        result = []
        for row in rows:
            # Construir entity temporal desde row
            type_entity = GeoDivisionTypeEntity()
            type_entity.id = row.id
            type_entity.name = row.name
            type_entity.label = row.label
            
            # Mapear usando mapper
            result.append(
                map_to_geo_division_type_by_country_response(
                    type_entity=type_entity,
                    level=row.level,
                    count=row.count,
                )
            )
        
        return result
```

**Patrón del método `execute`:**
1. Recibe `config: Config` y `params: XXXRequest`
2. Retorna `Union[XXXResponse, str]` (respuesta o mensaje de error)
3. Valida inputs y resultados
4. Propaga errores como strings
5. Mapea entities a response models
6. Retorna response model o lista de response models

### Paso 6: Crear Controller

**Ubicación:** `src/infrastructure/web/controller/business/{modulo}_controller.py`

```python
# geography_controller.py
from typing import List
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.response import Response
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.geography.index import (
    TypesByCountryRequest,
    GeoDivisionTypeByCountryResponse,
)
from src.domain.services.use_cases.business.geography.types_by_country.types_by_country_use_case import (
    TypesByCountryUseCase,
)

class GeographyController:
    def __init__(self) -> None:
        self.types_by_country_use_case = TypesByCountryUseCase()
        self.message = Message()

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def types_by_country(
        self, config: Config, params: TypesByCountryRequest
    ) -> Response[List[GeoDivisionTypeByCountryResponse]]:  # ← Tipo específico
        result = await self.types_by_country_use_case.execute(config, params)
        
        if isinstance(result, str):
            return Response.error(None, result)
        
        return Response.success_temporary_message(
            response=result,
            message=await self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=KEYS_MESSAGES.CORE_QUERY_MADE.value),
            ),
        )
```

**Patrón del controller:**
1. Inicializar todos los use cases en `__init__`
2. Cada método recibe `config: Config, params: XXXRequest`
3. Retorna `Response[T]` con tipo genérico específico
4. Invoca use case y verifica si el resultado es error (string)
5. Construye `Response.error()` o `Response.success_temporary_message()`
6. Incluye mensaje localizado

### Paso 7: Crear Router

**Ubicación:** `src/infrastructure/web/business_routes/{modulo}_router.py`

```python
# geography_router.py
from typing import List
from src.core.config import settings
from src.core.models.config import Config
from src.core.models.response import Response
from fastapi import APIRouter, Depends, status
from src.core.methods.get_config import get_config
from src.core.wrappers.execute_transaction import execute_transaction_route
from src.domain.models.business.geography.index import (
    TypesByCountryRequest,
    GeoDivisionTypeByCountryResponse,
)
from src.infrastructure.web.controller.business.geography_controller import (
    GeographyController,
)

geography_router = APIRouter(
    prefix="/geography",  # ← URL prefix
    tags=["Geography"],    # ← Tag para Swagger (diferente a entidad)
    responses={404: {"description": "Not found"}},
)

geography_controller = GeographyController()

@geography_router.post(
    "/country/types",  # ← Ruta relativa
    status_code=status.HTTP_200_OK,
    response_model=Response[List[GeoDivisionTypeByCountryResponse]],  # ← Tipo específico
    summary="Tipos de división por país",  # ← Título para Swagger
    description="""
    Obtiene todos los tipos de división geográfica disponibles...
    
    **Caso de uso:**
    - Mostrar estructura geográfica
    - Obtener estadísticas
    
    **Respuesta incluye:**
    - ID, nombre, label, level, count
    """,  # ← Descripción detallada
)
@execute_transaction_route(enabled=settings.has_track)
async def types_by_country(
    params: TypesByCountryRequest,  # ← Clase Request con nombre params
    config: Config = Depends(get_config)
) -> Response[List[GeoDivisionTypeByCountryResponse]]:  # ← Tipo específico
    return await geography_controller.types_by_country(config=config, params=params)
```

**Patrón del router:**
1. Crear `APIRouter` con `prefix` y `tags` únicos
2. Instanciar controller **una sola vez** fuera de las funciones
3. Cada endpoint:
   - Decorador con `summary` y `description`
   - Parámetro `params: XXXRequest` (nombre SIEMPRE `params`)
   - Parámetro `config: Config = Depends(get_config)`
   - Retorno `Response[T]` con tipo específico
4. Delegar todo el trabajo al controller

**Métodos HTTP:**
- `POST`: Para operaciones con body (mayoría de business endpoints)
- `GET`: Para consultas simples sin parámetros (ej: `/countries`)
- `DELETE`: Raramente usado en business (usar `POST` con flag de acción)

### Paso 8: Registrar el Router

**Ubicación:** `src/infrastructure/web/routes/route_business.py`

```python
from src.infrastructure.web.business_routes.geography_router import geography_router

class RouteBusiness:
    @staticmethod
    def set_routes(app):
        app.include_router(geography_router)
        # ... otros routers
```

### Paso 9: Verificar el Stack Completo

Checklist de archivos creados para el módulo `geography`:

```
✅ Modelos:
   - src/domain/models/business/geography/types_by_country_request.py
   - src/domain/models/business/geography/geo_division_type_by_country_response.py
   - src/domain/models/business/geography/index.py

✅ Use Cases:
   - src/domain/services/use_cases/business/geography/types_by_country/types_by_country_use_case.py
   - src/domain/services/use_cases/business/geography/types_by_country/__init__.py

✅ Repository (si necesitas):
   - src/infrastructure/database/repositories/business/geography_repository.py

✅ Mappers (si necesitas):
   - src/infrastructure/database/repositories/business/mappers/geography/geography_mapper.py

✅ Controller:
   - src/infrastructure/web/controller/business/geography_controller.py

✅ Router:
   - src/infrastructure/web/business_routes/geography_router.py

✅ Registro:
   - src/infrastructure/web/routes/route_business.py (include_router)
```

### Paso 10: Probar el Endpoint

1. **Reiniciar servidor** si es necesario
2. **Ir a Swagger**: `http://localhost:8000/docs`
3. **Verificar** que aparece el tag "Geography" con el endpoint
4. **Probar** con datos reales usando la interfaz de Swagger
5. **Verificar response** y ajustar si es necesario

### Ejemplo Completo Mínimo

**Módulo más simple posible** (consulta de lectura):

```
geography/
├── models/business/geography/
│   ├── countries_response.py       # Solo response (GET sin body)
│   └── index.py
├── use_cases/business/geography/
│   └── countries/
│       └── countries_use_case.py   # Lógica simple
├── controller/business/
│   └── geography_controller.py     # Delegación
└── business_routes/
    └── geography_router.py         # Endpoint GET
```

**Código mínimo:**

```python
# countries_use_case.py (20 líneas)
class CountriesUseCase:
    def __init__(self):
        self.geo_division_repository = GeoDivisionRepository()
        self.message = Message()

    async def execute(self, config: Config) -> Union[List[GeoDivisionItemResponse], str]:
        countries = await self.geo_division_repository.list(
            config=config,
            params=Pagination(filters=[{"field": "level", "value": 0}])
        )
        if not countries:
            return await self.message.get_message(...)
        return [map_to_response(c) for c in countries]

# geography_controller.py (15 líneas)
class GeographyController:
    def __init__(self):
        self.countries_use_case = CountriesUseCase()
        self.message = Message()

    async def countries(self, config: Config) -> Response[List[GeoDivisionItemResponse]]:
        result = await self.countries_use_case.execute(config)
        if isinstance(result, str):
            return Response.error(None, result)
        return Response.success_temporary_message(response=result, message=...)

# geography_router.py (15 líneas)
@geography_router.get(
    "/countries",
    response_model=Response[List[GeoDivisionItemResponse]],
    summary="Listar países",
    description="Obtiene todos los países disponibles..."
)
async def countries(config: Config = Depends(get_config)) -> Response[List[GeoDivisionItemResponse]]:
    return await geography_controller.countries(config)
```

**Total:** ~50 líneas de código para un endpoint funcional completo.

---

## Referencias

- **[02] Entity Flow**: Documentación de CRUD estándar para entidades simples
- **[03-05] Auth Flow Specification**: Ejemplo completo del flujo de autenticación
- **[05] Arquitectura General**: Capas, separación de responsabilidades, principios SOLID

**Documentación relacionada:**
- Convenciones de código y estilo
- Guía de migrations (Liquibase)
- Manejo de errores y mensajes localizados
- Configuración de permisos y decoradores

---

## Historial de Cambios

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0 | Nov 2024 | Creación inicial del documento de Business Flow | Equipo de Desarrollo Goluti |
| 1.1 | Nov 12, 2024 | Agregada sección 7.6 "Organización de Use Cases en Business": Cada flujo de negocio tiene su propia carpeta dentro de auth/ con todos sus casos de uso (principal + auxiliares). Incluye ejemplos de estructura, nomenclatura e imports. | Equipo de Desarrollo Goluti |
| 1.2 | Ene 23, 2026 | Actualizada sección 7.6: Documentado patrón completo para módulos de negocio. Agregado: estructura por módulo (auth, geography), convención de nomenclatura sin prefijos redundantes, stack completo por módulo (router → controller → use cases → repository → mapper → models), tabla de rutas por capa, nota sobre separación de tags en Swagger. | Equipo de Desarrollo Goluti |
| 2.0 | Ene 23, 2026 | **Refactorización completa como especificación de construcción**: Eliminada sección de "Casos de Uso Disponibles" (listado de endpoints específicos). Documento reenfocado como guía de "cómo construir" flujos de negocio. Agregadas secciones 6.7 (Tipos Genéricos en Response), 6.8 (Documentación de Swagger). Nueva sección 7: "Guía: Crear un Nuevo Módulo de Negocio" con paso a paso completo, ejemplos de código, checklist y ejemplo mínimo de 50 líneas. Documento ahora es prescriptivo, no descriptivo. | Equipo de Desarrollo Goluti |

---

**Fin del Documento**


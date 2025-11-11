# Componentes Core - Overview

**Versión**: 1.0  
**Fecha**: Noviembre 2024  
**Estado**: Vigente  
**Autor(es)**: Equipo de Desarrollo Goluti

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Propósito de Core](#propósito-de-core)
3. [Estructura de Core](#estructura-de-core)
4. [Componentes Principales](#componentes-principales)
5. [Uso Transversal](#uso-transversal)
6. [Referencias](#referencias)

---

## Introducción

La capa **Core** (`src/core/`) contiene todos los componentes transversales y utilidades que son utilizados por todas las demás capas del sistema (Domain e Infrastructure). Estos componentes implementan **cross-cutting concerns** como configuración, middleware, decoradores, tipos enumerados y modelos compartidos.

### Principio de Diseño

- **Independiente del dominio**: No conoce entidades específicas de negocio
- **Reutilizable**: Usado por Entity y Business flows
- **Sin lógica de negocio**: Solo infraestructura técnica
- **Configurable**: Adaptable a diferentes entornos

---

## Propósito de Core

### Cross-Cutting Concerns

Los componentes core resuelven preocupaciones transversales:

1. **Configuración**: Gestión de variables de entorno y settings
2. **Middleware**: Interceptación de requests/responses HTTP
3. **Decoradores (Wrappers)**: Funcionalidad aplicable a múltiples métodos
4. **Tipos y Enums**: Tipos compartidos por todo el sistema
5. **Modelos Comunes**: Estructuras de datos reutilizables
6. **Utilidades**: Clases helper (Token, Password, Message)

---

## Estructura de Core

```
src/core/
├── __init__.py
├── config.py                    # Configuración principal del sistema
│
├── classes/                     # Clases auxiliares
│   ├── async_message.py         # Gestión de mensajes localizados
│   ├── bearer.py                # Autenticación Bearer
│   ├── password.py              # Hashing y validación de contraseñas
│   └── token.py                 # Generación y validación de JWT
│
├── enums/                       # Tipos enumerados
│   ├── __init__.py
│   ├── condition_type.py        # Tipos de condiciones de filtros
│   ├── context.py               # Contextos de aplicación
│   ├── keys_message.py          # Keys de mensajes localizados
│   ├── language.py              # Códigos de idioma
│   ├── layer.py                 # Capas de arquitectura (tracking)
│   ├── message_type.py          # Tipos de mensaje (temporary/static)
│   ├── notification_type.py     # Tipos de notificación (success/error/warning)
│   ├── permission_type.py       # Tipos de permisos
│   └── response_type.py         # Tipos de respuesta (object/dict)
│
├── methods/                     # Métodos utilitarios
│   ├── __init__.py
│   ├── apply_memory_filters.py  # Aplicación de filtros en memoria
│   ├── build_alias_map.py       # Construcción de mapas de alias
│   ├── get_config.py            # Extracción de configuración de request
│   ├── get_filter.py            # Construcción de filtros SQLAlchemy
│   └── get_filter_with_alias.py # Filtros con alias de tablas
│
├── middleware/                  # Middleware de FastAPI
│   ├── __init__.py
│   ├── cors_app.py              # Configuración de CORS
│   ├── redirect_to_docs.py      # Redirección a /docs
│   └── user_rate_limit_middleware.py  # Rate limiting
│
├── models/                      # Modelos Pydantic compartidos
│   ├── __init__.py
│   ├── access_token.py          # Modelo de access token JWT
│   ├── access_token_api.py      # Modelo de API token
│   ├── base.py                  # Modelo base
│   ├── config.py                # Modelo de configuración
│   ├── filter.py                # Modelos de filtrado y paginación
│   ├── message.py               # Modelos de mensajes
│   ├── params_ws.py             # Parámetros de WebSocket
│   ├── response.py              # Modelo de respuesta HTTP
│   └── ws_request.py            # Modelo de request WebSocket
│
└── wrappers/                    # Decoradores (AOP)
    ├── __init__.py
    ├── check_permissions.py     # Verificación de permisos
    ├── check_roles.py           # Verificación de roles
    └── execute_transaction.py   # Tracking de transacciones
```

---

## Componentes Principales

### 1. Configuration (`config.py`)

Gestiona toda la configuración del sistema usando variables de entorno:

```python
class Settings(BaseSettings):
    # Base de datos
    database_user: str
    database_password: str
    database_name: str
    database_host: str
    database_schema: str
    
    # Seguridad
    secret_key: str
    jwt_secret_key: str
    jwt_algorithm: str
    
    # Aplicación
    project_name: str
    project_version: str
    project_description: str
    app_environment: str  # pc, qa, prod
    
    # Features
    has_debug: bool
    has_track: bool  # Habilitar tracking de transacciones

settings = Settings()
```

**Uso:**
```python
from src.core.config import settings

if settings.has_track:
    # Habilitar tracking
    pass
```

### 2. Middleware

#### CORS Configuration (`cors_app.py`)
```python
class CorsAppConfigurator:
    @staticmethod
    def setup_cors(app: FastAPI):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
```

#### Rate Limiting (`user_rate_limit_middleware.py`)
Limita el número de requests por usuario/IP.

#### Redirect to Docs (`redirect_to_docs.py`)
Redirige "/" a "/docs" automáticamente.

### 3. Wrappers (Decoradores)

#### Check Permissions (`@check_permissions`)
```python
@check_permissions([PERMISSION_TYPE.SAVE.value])
async def save(params: UserSave, config: Config = Depends(get_config)):
    # Solo ejecuta si el usuario tiene permiso SAVE
    pass
```

**Funcionalidad:**
- Valida token JWT del header Authorization
- Extrae permisos del token
- Verifica que el usuario tenga los permisos requeridos
- Retorna 403 Forbidden si no tiene permisos

#### Execute Transaction (`@execute_transaction`)
```python
@execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
async def execute(self, config: Config, params: UserSave) -> Union[User, str, None]:
    # Tracking de transacción si enabled=True
    pass
```

**Funcionalidad:**
- Registra inicio y fin de operación
- Captura excepciones y errores
- Permite análisis de performance
- Trazabilidad completa de requests

### 4. Enums

#### Permission Types
```python
class PERMISSION_TYPE(str, Enum):
    SAVE = "save"
    UPDATE = "update"
    DELETE = "delete"
    READ = "read"
    LIST = "list"
```

#### Condition Types (Filtros)
```python
class CONDITION_TYPE(str, Enum):
    EQUALS = "=="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_THAN_OR_EQUAL_TO = ">="
    LESS_THAN_OR_EQUAL_TO = "<="
    DIFFERENT_THAN = "!="
    LIKE = "like"
    IN = "in"
```

#### Notification Types
```python
class NOTIFICATION_TYPE(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
```

### 5. Models

#### Response Model
```python
class Response(BaseModel, Generic[T]):
    message_type: MESSAGE_TYPE
    notification_type: NOTIFICATION_TYPE
    message: str
    response: Union[T, List[T], None]

    @classmethod
    def success_temporary_message(cls, response: T, message: str):
        return cls(
            message_type=MESSAGE_TYPE.TEMPORARY,
            notification_type=NOTIFICATION_TYPE.SUCCESS,
            message=message,
            response=response
        )

    @classmethod
    def error(cls, response: Any, message: str):
        return cls(
            message_type=MESSAGE_TYPE.STATIC,
            notification_type=NOTIFICATION_TYPE.ERROR,
            message=message,
            response=response
        )
```

#### Config Model
```python
class Config(BaseModel):
    async_db: Any  # Sesión de base de datos
    access_token: Optional[AccessToken] = None
    language: Optional[LANGUAGE] = LANGUAGE.ES
    response_type: Optional[RESPONSE_TYPE] = RESPONSE_TYPE.OBJECT
```

#### Filter and Pagination
```python
class FilterManager(BaseModel):
    field: str
    condition: CONDITION_TYPE
    value: Any
    group: Optional[int] = None

class Pagination(BaseModel):
    skip: Optional[int] = Field(default=None)
    limit: Optional[int] = Field(default=None)
    all_data: Optional[bool] = Field(default=False)
    filters: Optional[List[FilterManager]] = Field(default=None)
```

### 6. Classes (Utilities)

#### Token (`token.py`)
```python
class Token:
    def create_access_token(self, data: AccessToken) -> str:
        """Genera JWT access token"""
        to_encode = data.model_dump()
        expire = datetime.utcnow() + timedelta(minutes=data.token_expiration_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    def create_refresh_token(self, data: AccessToken) -> str:
        """Genera JWT refresh token"""
        # ...

    def validate_token(self, token: str) -> Union[AccessToken, None]:
        """Valida y decodifica JWT"""
        # ...
```

#### Password (`password.py`)
```python
class Password:
    def hash_password(self, password: str) -> str:
        """Hash password con bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica password contra hash"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
```

#### Message (`async_message.py`)
```python
class Message:
    async def get_message(
        self, config: Config, message: MessageCoreEntity
    ) -> str:
        """Obtiene mensaje localizado según idioma de config"""
        # Busca traducción en BD según key y language
        # Retorna mensaje localizado
        pass
```

### 7. Methods (Utilidades)

#### get_config (`get_config.py`)
```python
async def get_config(
    authorization: str = Header(None),
    language: str = Header(None),
) -> Config:
    """Extrae configuración del request HTTP"""
    # Crea sesión de BD
    # Valida y decodifica token
    # Retorna objeto Config
    pass

async def get_config_login(language: str = Header(None)) -> Config:
    """Config para login (sin token)"""
    pass
```

#### get_filter (`get_filter.py`)
```python
def get_filter(query, filters: List[FilterManager], entity) -> Query:
    """Aplica filtros a query SQLAlchemy"""
    # Itera sobre filters
    # Construye condiciones WHERE según CONDITION_TYPE
    # Maneja grupos (OR)
    # Retorna query modificado
    pass
```

---

## Uso Transversal

### En Entity Flow

```python
# Router
@user_router.post("", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.SAVE.value])  # ← Core wrapper
@execute_transaction_route(enabled=settings.has_track)  # ← Core wrapper
async def save(
    params: UserSave,
    config: Config = Depends(get_config)  # ← Core method
) -> Response:  # ← Core model
    return await user_controller.save(config=config, params=params)

# Use Case
class UserSaveUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.password = Password()  # ← Core class
        self.message = Message()  # ← Core class

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)  # ← Core wrapper
    async def execute(
        self, config: Config, params: UserSave  # ← Core model
    ) -> Union[User, str, None]:
        result.password = self.password.hash_password(result.password)  # ← Core class
        # ...
```

### En Business Flow

```python
# Router
@auth_router.post("/login", response_model=Response[AuthLoginResponse])
@execute_transaction_route(enabled=settings.has_track)  # ← Core wrapper
async def login(
    params: AuthLoginRequest,
    config: Config = Depends(get_config_login)  # ← Core method
) -> Response[AuthLoginResponse]:  # ← Core model
    return await auth_controller.login(config=config, params=params)

# Use Case
class AuthLoginUseCase:
    def __init__(self):
        self.token = Token()  # ← Core class
        self.message = Message()  # ← Core class

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)  # ← Core wrapper
    async def execute(
        self, config: Config, params: AuthLoginRequest  # ← Core model
    ) -> Union[AuthLoginResponse, str, None]:
        token = self.token.create_access_token(data=access_token)  # ← Core class
        # ...
```

---

## Referencias

- **[04-01] Configuration**: Especificación de configuración del sistema
- **[04-02] Middleware**: Especificación de middleware
- **[04-03] Wrappers**: Especificación de decoradores
- **[04-04] Enums**: Especificación de tipos enumerados
- **[04-05] Models**: Especificación de modelos compartidos
- **[04-06] Utilities**: Especificación de clases auxiliares

---

## Historial de Cambios

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0 | Nov 2024 | Creación inicial del documento de Core Components | Equipo de Desarrollo Goluti |

---

**Fin del Documento**


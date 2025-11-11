# Capas y Responsabilidades

**Versión**: 1.0  
**Fecha**: Noviembre 2024  
**Estado**: Vigente  
**Autor(es)**: Equipo de Desarrollo Goluti

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Reglas de Dependencia](#reglas-de-dependencia)
3. [Core Layer](#core-layer)
4. [Domain Layer](#domain-layer)
5. [Infrastructure Layer](#infrastructure-layer)
6. [Flujo de Dependencias](#flujo-de-dependencias)
7. [Referencias](#referencias)

---

## Introducción

La arquitectura del **Goluti Backend Platform** está organizada en **tres capas principales** siguiendo los principios de Clean Architecture. Cada capa tiene responsabilidades específicas y reglas de dependencia estrictas.

---

## Reglas de Dependencia

### Regla Fundamental

> **Las dependencias siempre apuntan hacia adentro, nunca hacia afuera**

```
┌─────────────────────────────────────┐
│      Infrastructure Layer           │
│  (Web, Database, External Services) │
└──────────────┬──────────────────────┘
               │ Depende de ↓
┌──────────────▼──────────────────────┐
│         Domain Layer                │
│  (Use Cases, Entities, Interfaces)  │
└──────────────┬──────────────────────┘
               │ Usa ↓
┌──────────────▼──────────────────────┐
│          Core Layer                 │
│    (Shared, Cross-cutting)          │
└─────────────────────────────────────┘
```

### Dependencias Permitidas

✅ **Permitido:**
- Infrastructure → Domain
- Infrastructure → Core
- Domain → Core
- Core → (nada, es autocontenido)

❌ **No Permitido:**
- Domain → Infrastructure
- Core → Domain
- Core → Infrastructure

---

## Core Layer

**Ubicación**: `src/core/`

### Responsabilidad

Proporcionar **componentes transversales** (cross-cutting concerns) utilizados por todas las capas:
- Configuración del sistema
- Middleware HTTP
- Decoradores (wrappers)
- Tipos y enumeraciones compartidas
- Modelos de datos comunes
- Utilidades generales

### Características

- **Independiente**: No depende de ninguna otra capa
- **Reutilizable**: Usado por Domain e Infrastructure
- **Sin lógica de negocio**: Solo infraestructura técnica
- **Framework-agnostic**: Podría usarse con otro framework

### Componentes Principales

#### 1. Configuration (`config.py`)
```python
class Settings(BaseSettings):
    database_user: str
    database_password: str
    jwt_secret_key: str
    # ...
```

**Responsabilidades:**
- Cargar variables de entorno
- Proporcionar configuración global
- Gestionar diferentes ambientes (pc, qa, prod)

#### 2. Middleware (`middleware/`)
```python
class CorsAppConfigurator:
    @staticmethod
    def setup_cors(app: FastAPI):
        # Configurar CORS
```

**Responsabilidades:**
- Interceptar requests/responses HTTP
- Aplicar políticas de seguridad (CORS, Rate Limiting)
- Redireccionar requests

#### 3. Wrappers (`wrappers/`)
```python
def check_permissions(required_permissions: List[str]):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Verificar permisos
```

**Responsabilidades:**
- Aplicar funcionalidad transversal (AOP)
- Verificar permisos y roles
- Tracking de transacciones
- Logging y auditoría

#### 4. Enums (`enums/`)
```python
class PERMISSION_TYPE(str, Enum):
    SAVE = "save"
    UPDATE = "update"
    # ...
```

**Responsabilidades:**
- Definir tipos constantes
- Evitar strings mágicos
- Proporcionar autocompletado

#### 5. Models (`models/`)
```python
class Response(BaseModel, Generic[T]):
    message_type: MESSAGE_TYPE
    notification_type: NOTIFICATION_TYPE
    message: str
    response: Union[T, List[T], None]
```

**Responsabilidades:**
- Modelos compartidos entre capas
- Estructuras de datos comunes
- Validación con Pydantic

#### 6. Classes (`classes/`)
```python
class Token:
    def create_access_token(self, data: AccessToken) -> str:
        # Generar JWT
```

**Responsabilidades:**
- Utilidades especializadas
- Generación de tokens
- Hash de contraseñas
- Gestión de mensajes

#### 7. Methods (`methods/`)
```python
async def get_config(
    authorization: str = Header(None),
    language: str = Header(None)
) -> Config:
    # Extraer configuración del request
```

**Responsabilidades:**
- Funciones utilitarias
- Extracción de configuración
- Construcción de filtros SQLAlchemy
- Procesamiento de alias

### Reglas de Core

✅ **Debe:**
- Ser genérico y reutilizable
- No conocer entidades de negocio específicas
- Ser testeable de forma aislada

❌ **No debe:**
- Tener lógica de negocio
- Conocer detalles de Infrastructure
- Depender de Domain

---

## Domain Layer

**Ubicación**: `src/domain/`

### Responsabilidad

Contener toda la **lógica de negocio** del sistema:
- Casos de uso (use cases)
- Modelos de dominio
- Interfaces de repositorios
- Reglas de negocio

### Características

- **Independiente de frameworks**: No conoce FastAPI, SQLAlchemy
- **Independiente de BD**: Usa interfaces, no implementaciones
- **Testeable**: Puede testearse sin Infrastructure
- **Núcleo del sistema**: Representa el negocio

### Componentes Principales

#### 1. Models (`models/`)

**Entities** (`models/entities/`)
```python
class User(BaseModel):
    id: UUID4
    email: EmailStr
    first_name: str
    # ... campos de dominio
```

**Responsabilidades:**
- Representar entidades del dominio
- Validaciones de negocio con Pydantic
- Modelos para diferentes operaciones (Save, Update, etc.)

**Business** (`models/business/`)
```python
class AuthLoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthLoginResponse(BaseModel):
    platform_configuration: PlatformConfiguration
    token: str
```

**Responsabilidades:**
- Modelos específicos de casos de uso complejos
- Request/Response de operaciones de negocio
- DTOs (Data Transfer Objects)

#### 2. Services - Use Cases (`services/use_cases/`)

**Entity Use Cases**
```python
class UserSaveUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
        self.password = Password()
        
    async def execute(
        self, config: Config, params: UserSave
    ) -> Union[User, str, None]:
        # 1. Validar datos
        # 2. Aplicar reglas de negocio
        # 3. Transformar datos (hash password)
        # 4. Invocar repositorio
        # 5. Retornar resultado
```

**Responsabilidades:**
- Implementar casos de uso del sistema
- Orquestar operaciones
- Aplicar reglas de negocio
- Validar precondiciones
- Transformar datos

**Business Use Cases**
```python
class AuthLoginUseCase:
    def __init__(self):
        self.validate_user_uc = AuthValidateUserUseCase()
        self.initial_data_uc = AuthInitialUserDataUseCase()
        # ... más use cases
        
    async def execute(
        self, config: Config, params: AuthLoginRequest
    ) -> Union[AuthLoginResponse, str, None]:
        # 1. Validar credenciales
        # 2. Cargar datos iniciales
        # 3. Obtener permisos
        # 4. Generar tokens
        # 5. Construir respuesta compleja
```

**Responsabilidades:**
- Orquestar múltiples use cases
- Implementar lógica de negocio compleja
- Componer respuestas complejas
- Manejar transacciones de negocio

#### 3. Services - Repositories (`services/repositories/`)

**Repository Interfaces**
```python
class IUserRepository(ABC):
    @abstractmethod
    async def save(self, config: Config, params: UserEntity) -> Union[User, None]:
        pass
    
    @abstractmethod
    async def list(self, config: Config, params: Pagination) -> Union[List[User], None]:
        pass
    
    # ... más operaciones
```

**Responsabilidades:**
- Definir contratos de persistencia
- Abstraer acceso a datos
- Permitir múltiples implementaciones
- Facilitar testing con mocks

### Reglas de Domain

✅ **Debe:**
- Contener toda la lógica de negocio
- Usar interfaces para persistencia
- Ser independiente de frameworks
- Ser testeable sin Infrastructure

❌ **No debe:**
- Conocer detalles de base de datos (SQLAlchemy)
- Conocer detalles HTTP (FastAPI)
- Depender de implementaciones concretas

---

## Infrastructure Layer

**Ubicación**: `src/infrastructure/`

### Responsabilidad

Proporcionar **implementaciones concretas** de infraestructura:
- Acceso a base de datos
- Exposición de APIs HTTP
- Integración con servicios externos
- Mapeo de datos

### Características

- **Depende de Domain**: Implementa interfaces del dominio
- **Framework-specific**: Conoce FastAPI, SQLAlchemy
- **Intercambiable**: Puede cambiar sin afectar Domain
- **Detalles técnicos**: Configuraciones, conexiones

### Componentes Principales

#### 1. Database (`database/`)

**Config** (`database/config/`)
```python
class AsyncDatabaseConfig:
    def __init__(self):
        self.database_url = f"postgresql+asyncpg://..."
        self.engine = create_async_engine(self.database_url)
        self.async_session = sessionmaker(...)
```

**Responsabilidades:**
- Configurar conexión a PostgreSQL
- Gestionar pool de conexiones
- Proporcionar sesiones asíncronas

**Entities** (`database/entities/`)
```python
class UserEntity(Base):
    __tablename__ = "user"  # ← Nombre de la tabla en BD (mismo que entity)
    __table_args__ = {"schema": settings.database_schema}
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    # ... columnas SQLAlchemy
```

**Responsabilidades:**
- Mapear tablas de base de datos
- Definir relaciones
- Configurar constraints

**Convención Importante:**
- El nombre de la Entity en el código corresponde **exactamente** al nombre de la tabla en PostgreSQL
- Ejemplo: `UserEntity` → tabla `user`, `UserLocationRolEntity` → tabla `user_location_rol`
- Solo cambia el formato: PascalCase (código) ↔ snake_case (base de datos)

**Mappers** (`database/mappers/`)
```python
def map_to_user(user_entity: UserEntity) -> User:
    """Database Entity → Domain Model"""
    return User(
        id=user_entity.id,
        email=user_entity.email,
        # ...
    )

def map_to_save_user_entity(user_save: UserSave) -> UserEntity:
    """Domain Model → Database Entity"""
    return UserEntity(
        email=user_save.email,
        # ...
    )
```

**Responsabilidades:**
- Convertir entre DB Entity y Domain Model
- Aislar detalles de persistencia del dominio
- Transformar estructuras de datos

**Repositories** (`database/repositories/`)
```python
class UserRepository(IUserRepository):
    async def save(self, config: Config, params: UserEntity) -> Union[User, None]:
        async with config.async_db as db:
            db.add(params)
            await db.commit()
            await db.refresh(params)
            return map_to_user(params)
    
    async def list(self, config: Config, params: Pagination) -> Union[List[User], None]:
        async with config.async_db as db:
            stmt = select(UserEntity)
            
            if params.filters:
                stmt = get_filter(stmt, params.filters, UserEntity)
            
            if not params.all_data:
                stmt = stmt.offset(params.skip).limit(params.limit)
            
            result = await db.execute(stmt)
            users = result.scalars().all()
            
            return map_to_list_user(users) if users else None
```

**Responsabilidades:**
- Implementar interfaces de repositorios
- Ejecutar queries SQLAlchemy
- Aplicar filtros
- Manejar transacciones de BD
- Mapear resultados

#### 2. Web (`web/`)

**Routes** (`web/routes/`)
```python
class Route:
    @staticmethod
    def set_routes(app: FastAPI):
        app.include_router(user_router)
        app.include_router(company_router)
        # ... registrar todos los routers
```

**Responsabilidades:**
- Configurar routers en FastAPI
- Organizar endpoints por módulo
- Separar rutas de entidades y negocio

**Controllers** (`web/controller/`)
```python
class UserController:
    def __init__(self):
        self.user_save_use_case = UserSaveUseCase(user_repository)
        self.user_list_use_case = UserListUseCase(user_repository)
        # ...
        
    async def save(self, config: Config, params: UserSave) -> Response:
        result = await self.user_save_use_case.execute(config, params)
        
        if isinstance(result, str):
            return Response.error(None, result)
        
        return Response.success_temporary_message(
            response=result,
            message=await self.message.get_message(...)
        )
```

**Responsabilidades:**
- Invocar use cases
- Construir respuestas HTTP
- Manejar errores y mensajes
- Obtener mensajes localizados

**Routers** (`web/*_routes/`)
```python
user_router = APIRouter(prefix="/user", tags=["User"])

@user_router.post("", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.SAVE.value])
@execute_transaction_route(enabled=settings.has_track)
async def save(
    params: UserSave,
    config: Config = Depends(get_config)
) -> Response:
    return await user_controller.save(config=config, params=params)
```

**Responsabilidades:**
- Definir endpoints HTTP
- Aplicar decoradores (permisos, tracking)
- Validar entrada con Pydantic
- Extraer configuración de headers
- Delegar a controllers

### Reglas de Infrastructure

✅ **Debe:**
- Implementar interfaces de Domain
- Manejar detalles técnicos
- Aislar frameworks del dominio

❌ **No debe:**
- Contener lógica de negocio
- Exponer detalles técnicos a Domain

---

## Flujo de Dependencias

### Flujo Completo de una Request

```
1. HTTP Request
   ↓
2. Router (Infrastructure/Web)
   - Valida Pydantic
   - Aplica decoradores
   - Extrae Config
   ↓
3. Controller (Infrastructure/Web)
   - Invoca Use Case
   ↓
4. Use Case (Domain)
   - Aplica lógica de negocio
   - Invoca Repository Interface
   ↓
5. Repository Implementation (Infrastructure/Database)
   - Ejecuta query SQLAlchemy
   - Mapea resultados
   ↓
6. Database (PostgreSQL)
   ↓
7. (Retorna por las capas)
   ↓
8. HTTP Response
```

### Inyección de Dependencias

```python
# Infrastructure crea implementaciones concretas
user_repository = UserRepository()  # Infrastructure

# Domain recibe interfaces
class UserSaveUseCase:
    def __init__(self, user_repository: IUserRepository):  # Domain Interface
        self.user_repository = user_repository

# Controller inyecta implementación
user_controller = UserController()  # Crea use cases con repo concreto
```

---

## Referencias

- **[01-00] Architecture Overview**: Visión general de arquitectura
- **[01-02] Project Structure**: Estructura de directorios
- **[02-00] Entity Flow Overview**: Flujo de entidades
- **[03-00] Business Flow Overview**: Flujo de negocio

---

## Historial de Cambios

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0 | Nov 2024 | Creación inicial | Equipo de Desarrollo Goluti |

---

**Fin del Documento**


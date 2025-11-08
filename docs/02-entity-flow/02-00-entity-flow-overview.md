# Flujo de Entidades (Entity Flow) - Overview

**Versión**: 1.0  
**Fecha**: Noviembre 2024  
**Estado**: Vigente  
**Autor(es)**: Equipo de Desarrollo Goluti

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [¿Qué es el Entity Flow?](#qué-es-el-entity-flow)
3. [Flujo de Datos Completo](#flujo-de-datos-completo)
4. [Operaciones CRUD](#operaciones-crud)
5. [Componentes del Flujo](#componentes-del-flujo)
6. [Entidades Disponibles](#entidades-disponibles)
7. [Convenciones y Estándares](#convenciones-y-estándares)
8. [Ejemplo Completo](#ejemplo-completo)
9. [Referencias](#referencias)

---

## Introducción

El **Entity Flow** (Flujo de Entidades) es uno de los dos flujos principales del Goluti Backend Platform. Este flujo implementa operaciones CRUD (Create, Read, Update, Delete, List) estándar sobre las entidades del dominio siguiendo los principios de Clean Architecture.

### Objetivo

Proporcionar una forma consistente, escalable y mantenible de:
- Gestionar entidades del dominio
- Aplicar validaciones de negocio
- Ejecutar operaciones de persistencia
- Controlar acceso y permisos
- Responder con formatos estandarizados

---

## ¿Qué es el Entity Flow?

El Entity Flow es un **patrón arquitectónico repetible** que se aplica a todas las entidades del sistema que requieren operaciones CRUD. Cada entidad sigue exactamente la misma estructura de capas y componentes, lo que facilita:

- **Consistencia**: Todas las entidades se comportan igual
- **Predecibilidad**: Los desarrolladores saben dónde encontrar cada componente
- **Escalabilidad**: Agregar nuevas entidades es trivial
- **Mantenibilidad**: Cambios en una capa afectan a todas las entidades por igual
- **Testing**: Patrón uniforme facilita pruebas automatizadas

---

## Flujo de Datos Completo

### Diagrama de Flujo

```
┌──────────────┐
│   Cliente    │
│   (HTTP)     │
└──────┬───────┘
       │ 1. HTTP Request (POST/GET/PUT/DELETE)
       │    Headers: Authorization, Language
       │    Body: Params (JSON)
       ▼
┌──────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                     │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Router (FastAPI)                                   │  │
│  │  - Valida esquema Pydantic                          │  │
│  │  - Extrae configuración (get_config)                │  │
│  │  - Aplica decoradores (@check_permissions)          │  │
│  │  - Invoca método del Controller                     │  │
│  └────────────────────────────────────────────────────┘  │
└───────────────────────┬──────────────────────────────────┘
                        │ 2. Config + Params
                        ▼
┌──────────────────────────────────────────────────────────┐
│               INFRASTRUCTURE WEB LAYER                    │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Controller                                         │  │
│  │  - Recibe Config y Params validados                │  │
│  │  - Invoca Use Case específico                       │  │
│  │  - Maneja resultado (éxito/error)                   │  │
│  │  - Construye Response wrapper                       │  │
│  │  - Obtiene mensajes localizados                     │  │
│  └────────────────────────────────────────────────────┘  │
└───────────────────────┬──────────────────────────────────┘
                        │ 3. Config + Params
                        ▼
┌──────────────────────────────────────────────────────────┐
│                      DOMAIN LAYER                         │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Use Case                                           │  │
│  │  - Aplica lógica de negocio                         │  │
│  │  - Valida reglas del dominio                        │  │
│  │  - Transforma datos (ej: hash password)             │  │
│  │  - Invoca Repository Interface                      │  │
│  │  - Retorna Domain Model o mensaje de error         │  │
│  └────────────────────────────────────────────────────┘  │
└───────────────────────┬──────────────────────────────────┘
                        │ 4. Config + Domain Entity
                        ▼
┌──────────────────────────────────────────────────────────┐
│             INFRASTRUCTURE DATABASE LAYER                 │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Repository Implementation                          │  │
│  │  - Ejecuta query SQLAlchemy                         │  │
│  │  - Aplica filtros (en List)                         │  │
│  │  - Mapea DB Entity → Domain Model                   │  │
│  │  - Maneja errores de BD                             │  │
│  └────────────────────────────────────────────────────┘  │
└───────────────────────┬──────────────────────────────────┘
                        │ 5. SQL Query
                        ▼
┌──────────────────────────────────────────────────────────┐
│                       DATABASE                            │
│                     (PostgreSQL)                          │
└───────────────────────┬──────────────────────────────────┘
                        │ 6. Result Set
                        ▼
                    (retorna por las capas)
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│                    HTTP Response                          │
│  {                                                        │
│    "message_type": "temporary",                           │
│    "notification_type": "success",                        │
│    "message": "Operación exitosa",                        │
│    "response": { ... }                                    │
│  }                                                        │
└──────────────────────────────────────────────────────────┘
```

---

## Operaciones CRUD

Cada entidad en el Entity Flow soporta **5 operaciones estándar**:

### 1. **Save** (Crear)
- **HTTP**: `POST /{entity}`
- **Permiso**: `PERMISSION_TYPE.SAVE`
- **Entrada**: Modelo `{Entity}Save`
- **Salida**: Entidad creada con ID generado
- **Ejemplo**: `POST /user`

### 2. **Update** (Actualizar)
- **HTTP**: `PUT /{entity}`
- **Permiso**: `PERMISSION_TYPE.UPDATE`
- **Entrada**: Modelo `{Entity}Update` (incluye ID)
- **Salida**: Entidad actualizada
- **Ejemplo**: `PUT /user`

### 3. **List** (Listar con Filtros)
- **HTTP**: `POST /{entity}/list`
- **Permiso**: `PERMISSION_TYPE.LIST`
- **Entrada**: `Pagination` (skip, limit, filters)
- **Salida**: Lista de entidades
- **Ejemplo**: `POST /user/list`

### 4. **Read** (Leer por ID)
- **HTTP**: `GET /{entity}/{id}`
- **Permiso**: `PERMISSION_TYPE.READ`
- **Entrada**: ID en URL
- **Salida**: Una entidad
- **Ejemplo**: `GET /user/123e4567-e89b-12d3-a456-426614174000`

### 5. **Delete** (Eliminar)
- **HTTP**: `DELETE /{entity}/{id}`
- **Permiso**: `PERMISSION_TYPE.DELETE`
- **Entrada**: ID en URL
- **Salida**: Entidad eliminada
- **Ejemplo**: `DELETE /user/123e4567-e89b-12d3-a456-426614174000`

---

## Componentes del Flujo

Cada entidad tiene los siguientes componentes en su flujo:

### 1. **Domain Models** (`src/domain/models/entities/{entity}/`)

Modelos Pydantic que representan la entidad en diferentes contextos:

- **`{entity}.py`**: Modelo de dominio principal (lectura)
- **`{entity}_save.py`**: Modelo para crear (sin ID, con validaciones)
- **`{entity}_update.py`**: Modelo para actualizar (con ID, campos opcionales)
- **`{entity}_read.py`**: Modelo de consulta por ID
- **`{entity}_delete.py`**: Modelo de eliminación por ID
- **`index.py`**: Exporta todos los modelos

**Ejemplo: User**
```python
# user.py - Modelo principal
class User(BaseModel):
    id: UUID4
    platform_id: UUID4
    email: EmailStr
    first_name: str
    last_name: str
    # ... más campos

# user_save.py - Crear
class UserSave(BaseModel):
    platform_id: UUID4
    email: EmailStr
    password: str  # será hasheado
    first_name: str
    # ... sin ID

# user_update.py - Actualizar
class UserUpdate(BaseModel):
    id: UUID4  # requerido
    platform_id: Optional[UUID4] = None
    email: Optional[EmailStr] = None
    # ... campos opcionales
```

### 2. **Use Cases** (`src/domain/services/use_cases/entities/{entity}/`)

Casos de uso que implementan la lógica de negocio:

- **`{entity}_save_use_case.py`**: Lógica para crear
- **`{entity}_update_use_case.py`**: Lógica para actualizar
- **`{entity}_list_use_case.py`**: Lógica para listar con filtros
- **`{entity}_read_use_case.py`**: Lógica para leer por ID
- **`{entity}_delete_use_case.py`**: Lógica para eliminar

**Ejemplo: UserSaveUseCase**
```python
class UserSaveUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
        self.message = Message()
        self.password = Password()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self, config: Config, params: UserSave
    ) -> Union[User, str, None]:
        # 1. Mapear a entidad de BD
        result = map_to_save_user_entity(params)
        
        # 2. Aplicar lógica de negocio (hash password)
        result.password = self.password.hash_password(result.password)
        
        # 3. Persistir
        result = await self.user_repository.save(config=config, params=result)
        
        # 4. Validar resultado
        if not result:
            return await self.message.get_message(...)
        
        # 5. Retornar en formato solicitado
        if config.response_type == RESPONSE_TYPE.OBJECT.value:
            return result
        elif config.response_type == RESPONSE_TYPE.DICT.value:
            return result.dict()
        
        return result
```

### 3. **Repository Interface** (`src/domain/services/repositories/entities/`)

Contrato (interfaz) que define operaciones de persistencia:

```python
# i_user_repository.py
class IUserRepository(ABC):
    @abstractmethod
    async def save(self, config: Config, params: UserEntity) -> Union[User, None]:
        pass

    @abstractmethod
    async def update(self, config: Config, params: UserUpdate) -> Union[User, None]:
        pass

    @abstractmethod
    async def list(self, config: Config, params: Pagination) -> Union[List[User], None]:
        pass

    @abstractmethod
    async def read(self, config: Config, params: UserRead) -> Union[User, None]:
        pass

    @abstractmethod
    async def delete(self, config: Config, params: UserDelete) -> Union[User, None]:
        pass
```

### 4. **Repository Implementation** (`src/infrastructure/database/repositories/entities/`)

Implementación concreta usando SQLAlchemy:

```python
class UserRepository(IUserRepository):
    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def save(self, config: Config, params: UserEntity) -> Union[User, None]:
        async with config.async_db as db:
            db.add(params)
            await db.commit()
            await db.refresh(params)
            return map_to_user(params)

    # ... otras operaciones
```

### 5. **Database Entity** (`src/infrastructure/database/entities/`)

Modelo SQLAlchemy que mapea a la tabla de BD:

```python
class UserEntity(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": settings.database_schema}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_id = Column(UUID(as_uuid=True), ForeignKey(...))
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    # ... más columnas
```

### 6. **Mappers** (`src/infrastructure/database/mappers/`)

Funciones que convierten entre DB Entity y Domain Model:

```python
def map_to_user(user_entity: UserEntity) -> User:
    """DB Entity → Domain Model"""
    return User(
        id=user_entity.id,
        platform_id=user_entity.platform_id,
        email=user_entity.email,
        # ... mapeo de todos los campos
    )

def map_to_save_user_entity(user_save: UserSave) -> UserEntity:
    """Domain Model → DB Entity (para crear)"""
    return UserEntity(
        platform_id=user_save.platform_id,
        email=user_save.email,
        password=user_save.password,
        # ...
    )
```

### 7. **Controller** (`src/infrastructure/web/controller/entities/`)

Orquesta los use cases y construye respuestas HTTP:

```python
class UserController:
    def __init__(self) -> None:
        self.user_save_use_case = UserSaveUseCase(user_repository)
        self.user_update_use_case = UserUpdateUseCase(user_repository)
        self.user_list_use_case = UserListUseCase(user_repository)
        self.user_delete_use_case = UserDeleteUseCase(user_repository)
        self.user_read_use_case = UserReadUseCase(user_repository)
        self.message = Message()

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def save(self, config: Config, params: UserSave) -> Response:
        result_save = await self.user_save_use_case.execute(config, params)
        
        if isinstance(result_save, str):
            return Response.error(None, result_save)
        
        return Response.success_temporary_message(
            response=result_save,
            message=await self.message.get_message(...)
        )
```

### 8. **Router** (`src/infrastructure/web/entities_routes/`)

Define los endpoints HTTP con FastAPI:

```python
user_router = APIRouter(
    prefix="/user", 
    tags=["User"],
    responses={404: {"description": "Not found"}}
)

user_controller = UserController()

@user_router.post("", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.SAVE.value])
@execute_transaction_route(enabled=settings.has_track)
async def save(params: UserSave, config: Config = Depends(get_config)) -> Response:
    return await user_controller.save(config=config, params=params)

@user_router.put("", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.UPDATE.value])
@execute_transaction_route(enabled=settings.has_track)
async def update(params: UserUpdate, config: Config = Depends(get_config)) -> Response:
    return await user_controller.update(config=config, params=params)

# ... más endpoints (list, read, delete)
```

---

## Entidades Disponibles

El sistema actualmente implementa el Entity Flow completo para las siguientes entidades:

| Entidad | Endpoint Base | Descripción |
|---------|---------------|-------------|
| **User** | `/user` | Usuarios del sistema |
| **Company** | `/company` | Empresas/Organizaciones |
| **Platform** | `/platform` | Configuración de plataforma |
| **Location** | `/location` | Ubicaciones/Sucursales |
| **Language** | `/language` | Idiomas soportados |
| **Currency** | `/currency` | Monedas del sistema |
| **Country** | `/country` | Países |
| **Menu** | `/menu` | Elementos de menú |
| **Permission** | `/permission` | Permisos del sistema |
| **Rol** | `/rol` | Roles de usuario |
| **ApiToken** | `/api_token` | Tokens de API |
| **Translation** | `/translation` | Traducciones de textos |
| **CurrencyLocation** | `/currency_location` | Monedas por ubicación |
| **MenuPermission** | `/menu_permission` | Permisos por menú |
| **RolPermission** | `/rol_permission` | Permisos por rol |
| **UserLocationRol** | `/user_location_rol` | Asignación de roles a usuarios |

---

## Convenciones y Estándares

### Nomenclatura

1. **Archivos**: 
   - `{entity}_save.py`, `{entity}_update.py`, etc.
   - Siempre en minúsculas con guiones bajos

2. **Clases**:
   - `UserSave`, `UserUpdate`, `UserSaveUseCase`, `UserRepository`
   - PascalCase

3. **Métodos**:
   - `save()`, `update()`, `list()`, `read()`, `delete()`
   - snake_case

4. **Nombres de Entidades**:
   - **Importante**: Los nombres de las entidades corresponden **exactamente** a los nombres de las tablas en la base de datos
   - Ejemplo: La entidad `User` mapea a la tabla `user` en PostgreSQL
   - Ejemplo: La entidad `UserLocationRol` mapea a la tabla `user_location_rol`
   - Esta convención mantiene consistencia entre el código y la base de datos
   - Formato: snake_case en base de datos → PascalCase en código Python

### Estructura de Respuesta

Todas las operaciones retornan el mismo formato:

```json
{
  "message_type": "temporary | static",
  "notification_type": "success | error | warning | info",
  "message": "Mensaje localizado",
  "response": { /* datos */ } | null
}
```

### Manejo de Errores

- **Use Case retorna `str`**: Error de lógica de negocio
- **Use Case retorna `None`**: Error de persistencia
- **Use Case retorna `Entity`**: Operación exitosa

### Decoradores Estándar

Todos los métodos de Router usan:
- `@check_permissions([PERMISSION_TYPE.xxx])`: Verifica permisos
- `@execute_transaction_route(enabled=...)`: Tracking de transacciones

---

## Ejemplo Completo

Ver documento **[02-06-entity-flow-examples.md]** para ejemplos completos de:
- Crear una nueva entidad desde cero
- Peticiones y respuestas HTTP reales
- Casos de uso comunes
- Manejo de errores

---

## Referencias

- **[02-01] Entity Models**: Especificación de modelos de dominio
- **[02-02] Entity Use Cases**: Especificación de casos de uso
- **[02-03] Entity Repositories**: Especificación de repositorios
- **[02-04] Entity Controllers**: Especificación de controladores
- **[02-05] Entity Routers**: Especificación de routers
- **[02-06] Entity Flow Examples**: Ejemplos prácticos completos
- **[06-03] List Services Specification**: Especificación del servicio List

---

## Historial de Cambios

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0 | Nov 2024 | Creación inicial del documento de Entity Flow | Equipo de Desarrollo Goluti |

---

**Fin del Documento**


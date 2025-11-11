# Entidades de Base de Datos (Database Entities)

**Versión**: 1.0  
**Fecha**: Noviembre 2024  
**Estado**: Vigente  
**Autor(es)**: Equipo de Desarrollo Goluti

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Convención de Nomenclatura](#convención-de-nomenclatura)
3. [Estructura de una Entity](#estructura-de-una-entity)
4. [Mapeo Entity a Tabla](#mapeo-entity-a-tabla)
5. [Listado Completo de Entities](#listado-completo-de-entities)
6. [Configuración de Schema](#configuración-de-schema)
7. [Referencias](#referencias)

---

## Introducción

Las **Database Entities** son clases SQLAlchemy que mapean directamente a las tablas de PostgreSQL. Estas entidades están ubicadas en `src/infrastructure/database/entities/` y representan la estructura física de la base de datos.

### Propósito

- Mapear tablas de PostgreSQL a objetos Python
- Definir columnas, tipos de datos y constraints
- Configurar relaciones entre tablas
- Proporcionar la capa de persistencia ORM

---

## Convención de Nomenclatura

### Regla Fundamental

> **Los nombres de las entidades corresponden EXACTAMENTE a los nombres de las tablas en PostgreSQL**

### Transformación de Nombres

| Capa | Formato | Ejemplo |
|------|---------|---------|
| **Domain Model** | PascalCase | `User`, `UserLocationRol` |
| **Database Entity** | PascalCase + "Entity" | `UserEntity`, `UserLocationRolEntity` |
| **Tabla PostgreSQL** | snake_case | `user`, `user_location_rol` |

### Ejemplos de Correspondencia

```python
# Entity en código (PascalCase)
class UserEntity(Base):
    __tablename__ = "user"  # ← Tabla en BD (snake_case)

class UserLocationRolEntity(Base):
    __tablename__ = "user_location_rol"  # ← Tabla en BD (snake_case)

class CurrencyLocationEntity(Base):
    __tablename__ = "currency_location"  # ← Tabla en BD (snake_case)
```

### ¿Por Qué Esta Convención?

✅ **Ventajas:**
- Consistencia entre código y base de datos
- Fácil mapeo mental (User → user)
- Sin ambigüedades en nombres
- Mantenibilidad del código
- Búsqueda rápida (el nombre te dice la tabla)

❌ **Sin esta convención:**
- Nombres arbitrarios dificultan el seguimiento
- Requiere documentación adicional
- Mayor probabilidad de errores

---

## Estructura de una Entity

### Template Básico

```python
from sqlalchemy import Column, String, Boolean, DateTime, UUID, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgreSQL_UUID
from src.core.config import settings
from src.infrastructure.database.config.async_config_db import Base
import uuid
from datetime import datetime

class [Entity]Entity(Base):
    """
    Entity que mapea la tabla [entity] en PostgreSQL.
    
    Tabla: platform.[entity]
    """
    
    # Configuración de tabla
    __tablename__ = "[entity]"  # ← Nombre exacto de la tabla
    __table_args__ = {"schema": settings.database_schema}  # ← Schema (platform)
    
    # Columnas
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # ... más columnas
    
    # Timestamps
    created_date = Column(DateTime, default=datetime.now)
    updated_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Estado
    state = Column(Boolean, default=True)
```

### Ejemplo Completo: UserEntity

```python
from sqlalchemy import Column, String, Boolean, DateTime, UUID, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgreSQL_UUID
from src.core.config import settings
from src.infrastructure.database.config.async_config_db import Base
import uuid
from datetime import datetime

class UserEntity(Base):
    """
    Entity que mapea la tabla user en PostgreSQL.
    
    Tabla: platform.user
    Descripción: Almacena información de usuarios del sistema
    """
    
    __tablename__ = "user"
    __table_args__ = {"schema": settings.database_schema}
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    platform_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{settings.database_schema}.platform.id"),
        nullable=False
    )
    
    # Datos del usuario
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)  # Hash bcrypt
    identification = Column(String(50), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # Refresh Token para autenticación
    refresh_token = Column(String(500), nullable=True)
    
    # Timestamps automáticos
    created_date = Column(DateTime, default=datetime.now)
    updated_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Estado del registro
    state = Column(Boolean, default=True)
```

---

## Mapeo Entity a Tabla

### Proceso de Mapeo

```
┌──────────────────────────┐
│   Domain Model (User)    │  ← Usado en lógica de negocio
└────────────┬─────────────┘
             │
             │ Mapper convierte
             ▼
┌──────────────────────────┐
│  Database Entity         │  ← Usado por SQLAlchemy
│  (UserEntity)            │
│  __tablename__ = "user"  │
└────────────┬─────────────┘
             │
             │ ORM mapea
             ▼
┌──────────────────────────┐
│  Tabla PostgreSQL        │  ← Estructura física
│  platform.user           │
└──────────────────────────┘
```

### Flujo de Datos

**Save (Crear):**
```
UserSave (Domain) 
  → Mapper 
  → UserEntity (Infrastructure)
  → SQLAlchemy INSERT
  → Tabla user (PostgreSQL)
```

**List (Listar):**
```
Tabla user (PostgreSQL)
  → SQLAlchemy SELECT
  → List[UserEntity] (Infrastructure)
  → Mapper
  → List[User] (Domain)
```

---

## Listado Completo de Entities

### Entities del Sistema

| Entity (Python) | Tabla (PostgreSQL) | Schema | Descripción |
|-----------------|-------------------|--------|-------------|
| `UserEntity` | `user` | platform | Usuarios del sistema |
| `CompanyEntity` | `company` | platform | Empresas/Organizaciones |
| `PlatformEntity` | `platform` | platform | Configuración de plataforma |
| `LocationEntity` | `location` | platform | Ubicaciones/Sucursales |
| `LanguageEntity` | `language` | platform | Idiomas soportados |
| `CurrencyEntity` | `currency` | platform | Monedas del sistema |
| `CountryEntity` | `country` | platform | Países |
| `MenuEntity` | `menu` | platform | Elementos de menú |
| `PermissionEntity` | `permission` | platform | Permisos del sistema |
| `RolEntity` | `rol` | platform | Roles de usuario |
| `ApiTokenEntity` | `api_token` | platform | Tokens de API |
| `TranslationEntity` | `translation` | platform | Traducciones de textos |
| `CurrencyLocationEntity` | `currency_location` | platform | Monedas por ubicación |
| `MenuPermissionEntity` | `menu_permission` | platform | Permisos por menú |
| `RolPermissionEntity` | `rol_permission` | platform | Permisos por rol |
| `UserLocationRolEntity` | `user_location_rol` | platform | Asignación de roles |

### Ubicación de Archivos

```
src/infrastructure/database/entities/
├── user_entity.py               # UserEntity → tabla user
├── company_entity.py            # CompanyEntity → tabla company
├── platform_entity.py           # PlatformEntity → tabla platform
├── location_entity.py           # LocationEntity → tabla location
├── language_entity.py           # LanguageEntity → tabla language
├── currency_entity.py           # CurrencyEntity → tabla currency
├── country_entity.py            # CountryEntity → tabla country
├── menu_entity.py               # MenuEntity → tabla menu
├── permission_entity.py         # PermissionEntity → tabla permission
├── rol_entity.py                # RolEntity → tabla rol
├── api_token_entity.py          # ApiTokenEntity → tabla api_token
├── translation_entity.py        # TranslationEntity → tabla translation
├── currency_location_entity.py  # CurrencyLocationEntity → tabla currency_location
├── menu_permission_entity.py    # MenuPermissionEntity → tabla menu_permission
├── rol_permission_entity.py     # RolPermissionEntity → tabla rol_permission
└── user_location_rol_entity.py  # UserLocationRolEntity → tabla user_location_rol
```

---

## Configuración de Schema

### Schema de Base de Datos

Todas las tablas están en el schema **`platform`**:

```python
from src.core.config import settings

class UserEntity(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": settings.database_schema}  # "platform"
```

### Variable de Entorno

```bash
# .env.pc / .env.qa / .env.prod
DATABASE_SCHEMA=platform
```

### Queries Generadas

```sql
-- SQLAlchemy genera queries con schema explícito
SELECT * FROM platform.user WHERE id = '...';
INSERT INTO platform.company (name, nit) VALUES ('...', '...');
UPDATE platform.location SET name = '...' WHERE id = '...';
```

---

## Tipos de Datos Comunes

### Mapeo de Tipos

| Tipo Python/SQLAlchemy | Tipo PostgreSQL | Ejemplo |
|------------------------|-----------------|---------|
| `UUID(as_uuid=True)` | `uuid` | IDs únicos |
| `String(N)` | `VARCHAR(N)` | Textos de longitud limitada |
| `Text` | `TEXT` | Textos largos |
| `Integer` | `INTEGER` | Números enteros |
| `Float` | `DOUBLE PRECISION` | Números decimales |
| `Boolean` | `BOOLEAN` | true/false |
| `DateTime` | `TIMESTAMP` | Fechas y horas |
| `JSON` | `JSON` | Datos JSON |
| `JSONB` | `JSONB` | Datos JSON indexables |

### Ejemplo de Tipos

```python
class ExampleEntity(Base):
    __tablename__ = "example"
    __table_args__ = {"schema": settings.database_schema}
    
    # UUID
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Strings
    email = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Numéricos
    age = Column(Integer, nullable=False)
    price = Column(Float, nullable=True)
    
    # Boolean
    active = Column(Boolean, default=True)
    
    # Fecha/Hora
    created_date = Column(DateTime, default=datetime.now)
    
    # JSON
    metadata = Column(JSONB, nullable=True)
```

---

## Foreign Keys y Relaciones

### Definición de Foreign Keys

```python
class UserLocationRolEntity(Base):
    __tablename__ = "user_location_rol"
    __table_args__ = {"schema": settings.database_schema}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys con schema explícito
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{settings.database_schema}.user.id"),
        nullable=False
    )
    
    location_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{settings.database_schema}.location.id"),
        nullable=False
    )
    
    rol_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{settings.database_schema}.rol.id"),
        nullable=False
    )
```

---

## Referencias

- **[01-02] Project Structure**: Estructura de archivos del proyecto
- **[01-03] Layers and Responsibilities**: Responsabilidades de Infrastructure Layer
- **[02-00] Entity Flow Overview**: Flujo completo de entidades
- **[05-03] Mappers**: Conversión entre Entity y Domain Model

---

## Historial de Cambios

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0 | Nov 2024 | Creación inicial - Documentación de Database Entities | Equipo de Desarrollo Goluti |

---

**Fin del Documento**


# Ejemplos Prácticos - Entity Flow

**Versión**: 1.0  
**Fecha**: Noviembre 2024  
**Estado**: Vigente  
**Autor(es)**: Equipo de Desarrollo Goluti

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Ejemplo Completo: Entidad User](#ejemplo-completo-entidad-user)
3. [Peticiones y Respuestas HTTP](#peticiones-y-respuestas-http)
4. [Casos de Uso Comunes](#casos-de-uso-comunes)
5. [Manejo de Errores](#manejo-de-errores)
6. [Agregar Nueva Entidad](#agregar-nueva-entidad)

---

## Introducción

Este documento proporciona ejemplos prácticos de implementación y uso del **Entity Flow**. Todos los ejemplos utilizan la entidad `User` pero los mismos patrones aplican para cualquier entidad del sistema.

---

## Ejemplo Completo: Entidad User

### 1. Save (Crear Usuario)

#### Request HTTP

```http
POST /user HTTP/1.1
Host: api.goluti.com
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Language: es

{
  "platform_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "nuevo.usuario@goluti.com",
  "password": "SecurePassword123",
  "identification": "12345678",
  "first_name": "Juan",
  "last_name": "Pérez",
  "phone": "+573001234567",
  "state": true
}
```

#### Response HTTP (Success)

```json
{
  "message_type": "temporary",
  "notification_type": "success",
  "message": "Información guardada exitosamente",
  "response": {
    "id": "987fcdeb-51a2-43d1-9f12-345678901234",
    "platform_id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "nuevo.usuario@goluti.com",
    "identification": "12345678",
    "first_name": "Juan",
    "last_name": "Pérez",
    "phone": "+573001234567",
    "state": true,
    "created_date": "2024-11-08T10:30:00Z",
    "updated_date": "2024-11-08T10:30:00Z"
  }
}
```

#### Código Python (Cliente)

```python
import httpx

async def create_user():
    url = "https://api.goluti.com/user"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "Language": "es",
        "Content-Type": "application/json"
    }
    payload = {
        "platform_id": "123e4567-e89b-12d3-a456-426614174000",
        "email": "nuevo.usuario@goluti.com",
        "password": "SecurePassword123",
        "identification": "12345678",
        "first_name": "Juan",
        "last_name": "Pérez",
        "phone": "+573001234567",
        "state": True
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        return response.json()
```

### 2. Update (Actualizar Usuario)

#### Request HTTP

```http
PUT /user HTTP/1.1
Host: api.goluti.com
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Language: es

{
  "id": "987fcdeb-51a2-43d1-9f12-345678901234",
  "platform_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "nuevo.usuario@goluti.com",
  "password": "SecurePassword123",
  "first_name": "Juan Carlos",
  "last_name": "Pérez García",
  "phone": "+573009876543",
  "state": true
}
```

**Nota**: En Update, los campos no especificados no se modifican, pero según la implementación actual todos los campos son requeridos.

#### Response HTTP (Success)

```json
{
  "message_type": "temporary",
  "notification_type": "success",
  "message": "Información actualizada exitosamente",
  "response": {
    "id": "987fcdeb-51a2-43d1-9f12-345678901234",
    "platform_id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "nuevo.usuario@goluti.com",
    "first_name": "Juan Carlos",
    "last_name": "Pérez García",
    "phone": "+573009876543",
    "state": true,
    "updated_date": "2024-11-08T11:45:00Z"
  }
}
```

### 3. List (Listar Usuarios con Filtros)

#### Request HTTP

```http
POST /user/list HTTP/1.1
Host: api.goluti.com
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Language: es

{
  "skip": 0,
  "limit": 10,
  "filters": [
    {
      "field": "state",
      "condition": "==",
      "value": true
    },
    {
      "field": "first_name",
      "condition": "like",
      "value": "Juan"
    }
  ]
}
```

#### Response HTTP (Success)

```json
{
  "message_type": "temporary",
  "notification_type": "success",
  "message": "Consulta realizada exitosamente",
  "response": [
    {
      "id": "987fcdeb-51a2-43d1-9f12-345678901234",
      "platform_id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "nuevo.usuario@goluti.com",
      "first_name": "Juan Carlos",
      "last_name": "Pérez García",
      "phone": "+573009876543",
      "state": true
    },
    {
      "id": "456789ab-cdef-1234-5678-90abcdef1234",
      "platform_id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "juan.lopez@goluti.com",
      "first_name": "Juan",
      "last_name": "López",
      "phone": "+573001111111",
      "state": true
    }
  ]
}
```

### 4. Read (Leer Usuario por ID)

#### Request HTTP

```http
GET /user/987fcdeb-51a2-43d1-9f12-345678901234 HTTP/1.1
Host: api.goluti.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Language: es
```

#### Response HTTP (Success)

```json
{
  "message_type": "temporary",
  "notification_type": "success",
  "message": "Consulta realizada exitosamente",
  "response": {
    "id": "987fcdeb-51a2-43d1-9f12-345678901234",
    "platform_id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "nuevo.usuario@goluti.com",
    "identification": "12345678",
    "first_name": "Juan Carlos",
    "last_name": "Pérez García",
    "phone": "+573009876543",
    "state": true,
    "created_date": "2024-11-08T10:30:00Z",
    "updated_date": "2024-11-08T11:45:00Z"
  }
}
```

### 5. Delete (Eliminar Usuario)

#### Request HTTP

```http
DELETE /user/987fcdeb-51a2-43d1-9f12-345678901234 HTTP/1.1
Host: api.goluti.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Language: es
```

#### Response HTTP (Success)

```json
{
  "message_type": "temporary",
  "notification_type": "success",
  "message": "Eliminación realizada exitosamente",
  "response": {
    "id": "987fcdeb-51a2-43d1-9f12-345678901234",
    "email": "nuevo.usuario@goluti.com",
    "first_name": "Juan Carlos",
    "last_name": "Pérez García"
  }
}
```

---

## Peticiones y Respuestas HTTP

### Headers Requeridos

Todas las peticiones requieren:

```http
Authorization: Bearer <access_token>
Language: es | en
Content-Type: application/json
```

**Excepciones:**
- `GET` y `DELETE` no requieren `Content-Type`

### Códigos de Estado HTTP

| Código | Descripción | Cuándo |
|--------|-------------|--------|
| **200 OK** | Operación exitosa | Siempre (incluso en errores de negocio) |
| **400 Bad Request** | Validación de Pydantic falló | Body JSON inválido |
| **401 Unauthorized** | Token inválido o expirado | Token JWT no válido |
| **403 Forbidden** | Sin permisos | Usuario no tiene permiso requerido |
| **404 Not Found** | Ruta no encontrada | Endpoint no existe |
| **422 Unprocessable Entity** | Validación de datos falló | Pydantic validation error |
| **500 Internal Server Error** | Error del servidor | Excepción no capturada |

### Formato de Respuesta de Error

```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "Descripción del error",
  "response": null
}
```

---

## Casos de Uso Comunes

### Caso 1: Búsqueda de Usuarios Activos por Nombre

```json
POST /user/list

{
  "filters": [
    {
      "field": "state",
      "condition": "==",
      "value": true
    },
    {
      "field": "first_name",
      "condition": "like",
      "value": "María"
    }
  ]
}
```

### Caso 2: Paginación de Usuarios

```json
POST /user/list

{
  "skip": 20,
  "limit": 10,
  "filters": [
    {
      "field": "state",
      "condition": "==",
      "value": true
    }
  ]
}
```

**Explicación**: Obtiene 10 usuarios (registros 21-30), solo activos.

### Caso 3: Usuarios de una Plataforma Específica

```json
POST /user/list

{
  "all_data": true,
  "filters": [
    {
      "field": "platform_id",
      "condition": "==",
      "value": "123e4567-e89b-12d3-a456-426614174000"
    }
  ]
}
```

**Nota**: `all_data: true` retorna todos los registros sin paginación.

### Caso 4: Usuarios con Múltiples Criterios OR

```json
POST /user/list

{
  "filters": [
    {
      "field": "first_name",
      "condition": "==",
      "value": "Juan",
      "group": 1
    },
    {
      "field": "first_name",
      "condition": "==",
      "value": "María",
      "group": 1
    },
    {
      "field": "state",
      "condition": "==",
      "value": true
    }
  ]
}
```

**SQL Equivalente**: `WHERE (first_name = 'Juan' OR first_name = 'María') AND state = true`

### Caso 5: Actualización Parcial (Soft Delete)

```json
PUT /user

{
  "id": "987fcdeb-51a2-43d1-9f12-345678901234",
  "platform_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "usuario@goluti.com",
  "password": "password_hash",
  "state": false  // Desactivar usuario sin eliminarlo
}
```

---

## Manejo de Errores

### Error: Email Duplicado

```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "El email ya está registrado en el sistema",
  "response": null
}
```

### Error: Usuario No Encontrado

```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "Usuario no encontrado",
  "response": null
}
```

### Error: Sin Permisos

```http
HTTP/1.1 403 Forbidden

{
  "message_type": "static",
  "notification_type": "error",
  "message": "No tiene permisos para realizar esta acción",
  "response": null
}
```

### Error: Token Expirado

```http
HTTP/1.1 401 Unauthorized

{
  "detail": "Token has expired"
}
```

### Error: Validación de Pydantic

```http
HTTP/1.1 422 Unprocessable Entity

{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## Agregar Nueva Entidad

### Paso a Paso: Entidad "Product"

#### 1. Domain Models (`src/domain/models/entities/product/`)

```python
# product.py
from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional

class Product(BaseModel):
    id: UUID4
    company_id: UUID4
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    active: bool
    created_date: datetime
    updated_date: datetime

# product_save.py
class ProductSave(BaseModel):
    company_id: UUID4
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    active: bool = True

# product_update.py
class ProductUpdate(BaseModel):
    id: UUID4
    company_id: UUID4
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    active: bool

# product_read.py
class ProductRead(BaseModel):
    id: UUID4

# product_delete.py
class ProductDelete(BaseModel):
    id: UUID4

# index.py
from .product import Product
from .product_save import ProductSave
from .product_update import ProductUpdate
from .product_read import ProductRead
from .product_delete import ProductDelete

__all__ = ["Product", "ProductSave", "ProductUpdate", "ProductRead", "ProductDelete"]
```

#### 2. Repository Interface (`src/domain/services/repositories/entities/`)

```python
# i_product_repository.py
from abc import ABC, abstractmethod
from typing import Union, List
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.domain.models.entities.product.index import (
    Product, ProductSave, ProductUpdate, ProductRead, ProductDelete
)
from src.infrastructure.database.entities.product_entity import ProductEntity

class IProductRepository(ABC):
    @abstractmethod
    async def save(self, config: Config, params: ProductEntity) -> Union[Product, None]:
        pass

    @abstractmethod
    async def update(self, config: Config, params: ProductUpdate) -> Union[Product, None]:
        pass

    @abstractmethod
    async def list(self, config: Config, params: Pagination) -> Union[List[Product], None]:
        pass

    @abstractmethod
    async def read(self, config: Config, params: ProductRead) -> Union[Product, None]:
        pass

    @abstractmethod
    async def delete(self, config: Config, params: ProductDelete) -> Union[Product, None]:
        pass
```

#### 3-8. Otros Componentes

Continuar con la misma estructura que User:
- Use Cases (5 archivos)
- Database Entity (SQLAlchemy)
- Mapper
- Repository Implementation
- Controller
- Router

**Ver código existente de User como referencia completa.**

---

## Referencias

- **[02-00] Entity Flow Overview**: Documentación completa del flujo
- **[06-03] List Services Specification**: Sistema de filtros detallado

---

## Historial de Cambios

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0 | Nov 2024 | Creación inicial | Equipo de Desarrollo Goluti |

---

**Fin del Documento**


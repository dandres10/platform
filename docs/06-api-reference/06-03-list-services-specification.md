# Especificación de Servicios List y Sistema de Filtros

**Versión**: 1.1  
**Fecha**: Noviembre 2024  
**Estado**: Vigente  
**Autor(es)**: Equipo de Desarrollo Goluti

---

## Tabla de Contenidos
1. [Introducción](#introducción)
2. [Arquitectura de Servicios List](#arquitectura-de-servicios-list)
3. [Estructura de Respuesta](#estructura-de-respuesta)
4. [Sistema de Filtros](#sistema-de-filtros)
5. [Ejemplos Prácticos](#ejemplos-prácticos)
6. [Referencia de API](#referencia-de-api)
7. [Casos de Uso Comunes](#casos-de-uso-comunes)

---

## Introducción

Los servicios de tipo `list` en la plataforma Goluti proporcionan funcionalidad de consulta y listado de entidades con capacidades avanzadas de filtrado, paginación y ordenamiento. Estos servicios siguen una arquitectura consistente basada en Clean Architecture y Domain-Driven Design.

---

## Arquitectura de Servicios List

### Flujo de Datos

```
HTTP Request → Router → Controller → UseCase → Repository → Database
                ↓
HTTP Response ← Response Wrapper ← Domain Entity ← Database Result
```

### Componentes Principales

#### 1. **Use Cases** (`src/domain/services/use_cases/entities/*/`)
- **Responsabilidad**: Lógica de negocio y orquestación
- **Patrón**: `{Entity}ListUseCase`
- **Método principal**: `execute(config: Config, params: Pagination)`

#### 2. **Controllers** (`src/infrastructure/web/controller/entities/`)
- **Responsabilidad**: Manejo de peticiones HTTP y respuestas
- **Patrón**: `{Entity}Controller`
- **Método**: `list(config: Config, params: Pagination)`

#### 3. **Routers** (`src/infrastructure/web/entities_routes/`)
- **Responsabilidad**: Definición de endpoints y validación
- **Endpoint**: `POST /{entity}/list`
- **Decoradores**: `@check_permissions`, `@execute_transaction_route`

#### 4. **Repositories** (`src/infrastructure/database/repositories/entities/`)
- **Responsabilidad**: Acceso a datos y aplicación de filtros
- **Método**: `list(config: Config, params: Pagination)`

---

## Estructura de Respuesta

### Tipo de Retorno de Use Cases

```python
Union[List[Entity], str, None]
```

- **`List[Entity]`**: Lista de entidades cuando hay resultados
- **`str`**: Mensaje de error o "sin resultados"
- **`None`**: Error crítico

### Wrapper de Respuesta HTTP

```python
class Response(BaseModel, Generic[T]):
    message_type: MESSAGE_TYPE           # Tipo de mensaje
    notification_type: NOTIFICATION_TYPE # Tipo de notificación
    message: str                        # Mensaje descriptivo
    response: Union[T, List[T], None]   # Datos de respuesta
```

### Tipos de Respuesta por Configuración

Dependiendo de `config.response_type`:

- **`RESPONSE_TYPE.OBJECT`** (por defecto): Objetos Pydantic
- **`RESPONSE_TYPE.DICT`**: Diccionarios Python

---

## Sistema de Filtros

### Modelo de Paginación

```python
class Pagination(BaseModel):
    skip: Optional[int] = Field(default=None)          # Offset para paginación
    limit: Optional[int] = Field(default=None)         # Límite de registros
    all_data: Optional[bool] = Field(default=False)    # Obtener todos los datos
    filters: Optional[List[FilterManager]] = Field(default=None)  # Lista de filtros
```

### Modelo de Filtro

```python
class FilterManager(BaseModel):
    field: str = Field(...)                    # Campo de la entidad a filtrar
    condition: CONDITION_TYPE = Field(...)     # Tipo de condición
    value: Any = Field(...)                    # Valor de comparación
    group: Optional[int] = Field(None)         # Grupo para operaciones OR
```

### Tipos de Condiciones

```python
class CONDITION_TYPE(str, Enum):
    EQUALS = "=="                    # Igualdad exacta
    GREATER_THAN = ">"              # Mayor que
    LESS_THAN = "<"                 # Menor que
    GREATER_THAN_OR_EQUAL_TO = ">=" # Mayor o igual que
    LESS_THAN_OR_EQUAL_TO = "<="    # Menor o igual que
    DIFFERENT_THAN = "!="           # Diferente de
    LIKE = "like"                   # Búsqueda de texto (contiene)
    IN = "in"                       # Pertenencia a lista
```

### Lógica de Filtros

#### Operaciones AND (por defecto)
Los filtros sin `group` se combinan con operador AND:

```python
# Filtros: field1 == value1 AND field2 > value2
filters = [
    {"field": "field1", "condition": "==", "value": "value1"},
    {"field": "field2", "condition": ">", "value": "value2"}
]
```

#### Operaciones OR (con grupos)
Los filtros con el mismo `group` se combinan con OR:

```python
# Filtros: (field1 == value1 OR field1 == value2) AND field3 > value3
filters = [
    {"field": "field1", "condition": "==", "value": "value1", "group": 1},
    {"field": "field1", "condition": "==", "value": "value2", "group": 1},
    {"field": "field3", "condition": ">", "value": "value3"}
]
```

### Validación de Filtros

- Solo se aplican filtros a **campos válidos** de la entidad
- Los campos se validan usando SQLAlchemy introspection
- Filtros con campos inválidos se ignoran silenciosamente

---

## Ejemplos Prácticos

### Ejemplo 1: Listado Simple con Paginación

**Petición:**
```json
POST /platform/list
{
  "skip": 0,
  "limit": 10
}
```

**Respuesta:**
```json
{
  "message_type": "temporary",
  "notification_type": "success",
  "message": "Consulta realizada exitosamente",
  "response": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "language_id": "987fcdeb-51a2-43d1-9f12-345678901234",
      "location_id": "456789ab-cdef-1234-5678-90abcdef1234",
      "currency_id": "789abcde-f012-3456-7890-abcdef123456",
      "token_expiration_minutes": 60,
      "refresh_token_expiration_minutes": 62
    }
  ]
}
```

### Ejemplo 2: Filtro por Igualdad

**Petición:**
```json
POST /user/list
{
  "filters": [
    {
      "field": "location_id",
      "condition": "==",
      "value": "456789ab-cdef-1234-5678-90abcdef1234"
    }
  ]
}
```

### Ejemplo 3: Filtros de Rango

**Petición:**
```json
POST /platform/list
{
  "filters": [
    {
      "field": "token_expiration_minutes",
      "condition": ">=",
      "value": 30
    },
    {
      "field": "token_expiration_minutes",
      "condition": "<=",
      "value": 120
    }
  ]
}
```

### Ejemplo 4: Búsqueda de Texto

**Petición:**
```json
POST /company/list
{
  "filters": [
    {
      "field": "name",
      "condition": "like",
      "value": "tecnología"
    }
  ]
}
```

### Ejemplo 5: Filtro IN (Múltiples Valores)

**Petición:**
```json
POST /user/list
{
  "filters": [
    {
      "field": "rol_id",
      "condition": "in",
      "value": [
        "admin-role-id",
        "manager-role-id",
        "supervisor-role-id"
      ]
    }
  ]
}
```

### Ejemplo 6: Filtros Complejos con OR

**Petición:**
```json
POST /platform/list
{
  "filters": [
    {
      "field": "language_id",
      "condition": "==",
      "value": "spanish-id",
      "group": 1
    },
    {
      "field": "language_id",
      "condition": "==",
      "value": "english-id",
      "group": 1
    },
    {
      "field": "token_expiration_minutes",
      "condition": ">",
      "value": 60
    }
  ]
}
```
*Busca plataformas donde: (idioma = español OR idioma = inglés) AND expiración > 60 minutos*

### Ejemplo 7: Obtener Todos los Datos

**Petición:**
```json
POST /language/list
{
  "all_data": true,
  "filters": [
    {
      "field": "active",
      "condition": "==",
      "value": true
    }
  ]
}
```

---

## Referencia de API

### Entidades Disponibles

Todas las siguientes entidades tienen servicios list disponibles:

- **Platform** (`/platform/list`)
- **User** (`/user/list`)
- **Company** (`/company/list`)
- **Location** (`/location/list`)
- **Language** (`/language/list`)
- **Currency** (`/currency/list`)
- **Country** (`/country/list`)
- **Menu** (`/menu/list`)
- **Permission** (`/permission/list`)
- **Rol** (`/rol/list`)
- **ApiToken** (`/api_token/list`)
- **Translation** (`/translation/list`)
- **CurrencyLocation** (`/currency_location/list`)
- **MenuPermission** (`/menu_permission/list`)
- **RolPermission** (`/rol_permission/list`)
- **UserLocationRol** (`/user_location_rol/list`)

### Headers Requeridos

```
Authorization: Bearer <token>
Language: <language-code>
Content-Type: application/json
```

### Códigos de Respuesta

- **200 OK**: Consulta exitosa
- **400 Bad Request**: Parámetros inválidos
- **401 Unauthorized**: Token inválido o expirado
- **403 Forbidden**: Sin permisos para listar
- **500 Internal Server Error**: Error del servidor

### Permisos Requeridos

Todos los endpoints de list requieren el permiso:
```
PERMISSION_TYPE.LIST.value
```

---

## Casos de Uso Comunes

### 1. Dashboard con Métricas

```json
POST /user/list
{
  "all_data": true,
  "filters": [
    {
      "field": "created_date",
      "condition": ">=",
      "value": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### 2. Búsqueda de Usuarios por Rol

```json
POST /user_location_rol/list
{
  "filters": [
    {
      "field": "rol_id",
      "condition": "==",
      "value": "admin-role-id"
    },
    {
      "field": "location_id",
      "condition": "==",
      "value": "headquarters-id"
    }
  ]
}
```

### 3. Listado Paginado para Tabla

```json
POST /company/list
{
  "skip": 20,
  "limit": 10,
  "filters": [
    {
      "field": "active",
      "condition": "==",
      "value": true
    }
  ]
}
```

### 4. Filtro de Exclusión

```json
POST /platform/list
{
  "filters": [
    {
      "field": "language_id",
      "condition": "!=",
      "value": null
    },
    {
      "field": "token_expiration_minutes",
      "condition": "!=",
      "value": 0
    }
  ]
}
```

### 5. Búsqueda Multi-criterio

```json
POST /translation/list
{
  "filters": [
    {
      "field": "language_id",
      "condition": "==",
      "value": "spanish-id"
    },
    {
      "field": "key",
      "condition": "like",
      "value": "error"
    },
    {
      "field": "active",
      "condition": "==",
      "value": true
    }
  ]
}
```

---

## Consideraciones de Rendimiento

### Mejores Prácticas

1. **Usar paginación** siempre que sea posible
2. **Filtrar por campos indexados** cuando sea posible
3. **Evitar `all_data: true`** en tablas grandes
4. **Usar filtros específicos** antes que búsquedas LIKE amplias

### Límites del Sistema

- **Límite por defecto**: 100 registros si no se especifica `limit`
- **Límite máximo**: 1000 registros por petición
- **Timeout**: 30 segundos para consultas complejas

---

## Manejo de Errores

### Errores Comunes

1. **Campo inválido**: El filtro se ignora silenciosamente
2. **Valor inválido para condición IN**: `ValueError` se lanza
3. **Sin resultados**: Retorna mensaje localizado
4. **Error de base de datos**: Retorna error genérico

### Estructura de Error

```json
{
  "message_type": "static",
  "notification_type": "error",
  "message": "Error en la consulta",
  "response": null
}
```

---

## Extensibilidad

### Agregar Nueva Entidad

Para agregar soporte de list a una nueva entidad:

1. Crear `{Entity}ListUseCase`
2. Implementar método `list` en `{Entity}Repository`
3. Agregar método `list` en `{Entity}Controller`
4. Definir ruta `POST /{entity}/list` en router
5. Configurar permisos apropiados

### Agregar Nueva Condición

Para agregar un nuevo tipo de condición:

1. Agregar valor a `CONDITION_TYPE` enum
2. Implementar lógica en `get_filter()` y `get_filter_with_alias()`
3. Actualizar `apply_memory_filters()` si es necesario
4. Documentar el nuevo tipo de condición

---

## Referencias

- **[02-00] Entity Flow Overview**: Documentación completa del flujo de entidades
- **[04-05] Core Models**: Modelos Filter y Pagination
- **[04-06] Core Utilities**: Método get_filter()

---

## Historial de Cambios

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0 | Oct 2024 | Versión inicial | Equipo Dev |
| 1.1 | Nov 2024 | Reorganización en nueva estructura de docs | Equipo Dev |

---

**Fin del Documento**


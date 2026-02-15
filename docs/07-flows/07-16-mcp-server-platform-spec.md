# 07-16: MCP Server - Platform

## Informacion del Documento

| Campo | Detalle |
|-------|---------|
| **Version** | 3.1 |
| **Fecha** | Febrero 13, 2026 |
| **Estado** | Implementado |
| **Autor(es)** | Equipo de Desarrollo Goluti |

---

## Tabla de Contenidos

1. [Objetivo](#objetivo)
2. [Que es MCP](#que-es-mcp)
3. [Alcance](#alcance)
4. [Arquitectura](#arquitectura)
5. [Tools Expuestos](#tools-expuestos)
6. [Autenticacion](#autenticacion)
7. [Estructura de Archivos](#estructura-de-archivos)
8. [Implementacion](#implementacion)
9. [Pruebas](#pruebas)
10. [Despliegue](#despliegue)
11. [Plan de Ejecucion](#plan-de-ejecucion)
12. [Riesgos](#riesgos)

---

## Objetivo

Agregar un endpoint `/mcp/business` a la app FastAPI de Platform que exponga los **flujos de negocio** (business routes) como tools MCP. Esto permite que cualquier cliente MCP (el futuro Chat Service u otros) consuma los servicios de autenticacion y geografia de la plataforma.

---

## Que es MCP

MCP (Model Context Protocol) es un protocolo abierto que estandariza como las aplicaciones AI consumen herramientas externas. El microservicio expone sus funciones como **tools** y cualquier cliente MCP puede descubrirlas y llamarlas via HTTP.

```
Cliente MCP  ──►  Platform /mcp/business  ──►  Tools  ──►  Endpoints REST  ──►  DB
```

---

## Alcance

### Incluido

Solo los **business routes** de `src/infrastructure/web/business_routes/`:

- `auth_router.py` → 13 tools
- `geography_router.py` → 7 tools

### Excluido

- Rutas CRUD de entidades (`src/infrastructure/web/entities_routes/`) - solo las necesita la UI de admin
- WebSocket routes

---

## Arquitectura

### Principio Clave: Tools como wrappers HTTP

Cada tool MCP es un **wrapper delgado** que llama al endpoint REST existente via `httpx`. No llama a controllers directamente. Esto garantiza que toda la cadena de FastAPI se ejecute: `Depends(get_config)`, `@check_permissions`, `@check_roles`, `@execute_transaction_route`, middleware.

```
┌─────────────────────────────────────────────────────────────┐
│  FastAPI App (main.py)                                      │
│                                                             │
│  ┌─────────────────┐       ┌────────────────────────────┐  │
│  │  MCP Server      │       │  Endpoints REST existentes │  │
│  │  /mcp/business   │       │                            │  │
│  │                  │ HTTP  │  POST /auth/login           │  │
│  │  tool: login ────┼──────►│  POST /auth/logout          │  │
│  │  tool: logout    │       │  GET  /geography/countries  │  │
│  │  tool: countries │       │  ...                        │  │
│  │  ...             │       │                            │  │
│  └─────────────────┘       │  Depends(get_config) ✅     │  │
│                             │  @check_permissions  ✅     │  │
│                             │  @execute_transaction ✅    │  │
│                             └──────────┬─────────────────┘  │
│                                        ▼                    │
│                                   Controllers               │
│                                        ▼                    │
│                                    Use Cases                │
│                                        ▼                    │
│                                   Repositories              │
│                                        ▼                    │
│                                   PostgreSQL                │
└─────────────────────────────────────────────────────────────┘
```

### Ventajas de este enfoque

- **No se necesita `config_builder.py`** - el endpoint REST ya maneja `Depends(get_config)`
- **Permisos y roles funcionan** - `@check_permissions`, `@check_roles` se ejecutan normalmente
- **Transaction tracking funciona** - `@execute_transaction_route` se ejecuta normalmente
- **Comportamiento identico** - la tool retorna exactamente lo mismo que el endpoint REST

### Nota sobre middlewares y `app.mount()`

`app.mount()` monta una sub-aplicacion ASGI independiente. Los middlewares de la app padre (CORS, rate limiting, `RedirectToDocsMiddleware`) **no se propagan** automaticamente a sub-aplicaciones montadas. Sin embargo, como el MCP server solo hace llamadas HTTP loopback a los endpoints REST (que si tienen middlewares), la cadena completa se ejecuta en el endpoint destino. El MCP server en si no necesita CORS ni rate limiting porque no es consumido directamente por el frontend.

---

## Tools Expuestos

### Auth (13 tools)

| # | Tool Name | Descripcion | Endpoint REST | Metodo | Auth |
|---|-----------|-------------|---------------|--------|------|
| 1 | `login` | Autenticar usuario en la plataforma | `/auth/login` | POST | No |
| 2 | `logout` | Cerrar sesion del usuario | `/auth/logout` | POST | Bearer |
| 3 | `refresh_token` | Renovar token JWT expirado | `/auth/refresh_token` | POST | Bearer |
| 4 | `create_api_token` | Generar API token de larga duracion | `/auth/create-api-token` | POST | Bearer |
| 5 | `create_user_internal` | Crear usuario interno (solo admin) | `/auth/create-user-internal` | POST | Bearer |
| 6 | `update_user_internal` | Actualizar datos de usuario interno | `/auth/update-user-internal/{user_id}` | PUT | Bearer |
| 7 | `delete_user_internal` | Eliminar usuario interno | `/auth/delete-user-internal/{user_id}` | DELETE | Bearer |
| 8 | `create_user_external` | Registrar usuario externo | `/auth/create-user-external` | POST | No |
| 9 | `delete_user_external` | Eliminar usuario externo | `/auth/delete-user-external/{user_id}` | DELETE | Bearer |
| 10 | `list_users_internal` | Listar usuarios internos con filtros | `/auth/users-internal` | POST | Bearer |
| 11 | `list_users_external` | Listar usuarios externos con filtros | `/auth/users-external` | POST | Bearer |
| 12 | `create_company` | Crear compania completa (menus, roles, permisos) | `/auth/create-company` | POST | No |
| 13 | `delete_company` | Eliminar compania y datos asociados | `/auth/delete-company/{company_id}` | DELETE | Bearer |

### Geography (7 tools)

| # | Tool Name | Descripcion | Endpoint REST | Metodo | Auth |
|---|-----------|-------------|---------------|--------|------|
| 1 | `get_countries` | Listar paises disponibles | `/geography/countries` | GET | No |
| 2 | `get_types_by_country` | Tipos de division de un pais | `/geography/country/types` | POST | No |
| 3 | `get_divisions_by_country_type` | Divisiones por pais y tipo | `/geography/country/type` | POST | No |
| 4 | `get_children` | Hijos directos de una division | `/geography/children` | POST | No |
| 5 | `get_children_by_type` | Descendientes recursivos por tipo | `/geography/children/type` | POST | No |
| 6 | `get_hierarchy` | Cadena de ancestros de una division | `/geography/hierarchy` | POST | No |
| 7 | `get_division_detail` | Detalle de una division geografica | `/geography/detail` | POST | No |

**Total: 20 tools**

---

## Autenticacion

El token JWT del usuario se pasa en los headers de la conexion MCP. El Chat Service (futuro) conecta al MCP con el token del usuario autenticado. Cada tool lo extrae del contexto MCP y lo envia al endpoint REST como `Authorization: Bearer`.

```
Frontend          Chat Service              MCP Server              REST Endpoint
   │                   │                        │                        │
   │── login ─────────►│                        │                        │
   │◄── token ─────────│                        │                        │
   │                   │                        │                        │
   │── chat msg ──────►│                        │                        │
   │  (con token)      │── connect MCP ────────►│                        │
   │                   │   headers: Bearer tok  │                        │
   │                   │                        │                        │
   │                   │── call tool ──────────►│── httpx.post ─────────►│
   │                   │   "list_users_internal" │   Authorization: tok  │
   │                   │                        │   language: ES         │
   │                   │                        │◄── JSON response ──────│
   │                   │◄── tool result ────────│                        │
```

Los tools publicos (geography) no necesitan token.

---

## Estructura de Archivos

```
src/
├── core/
│   └── classes/
│       └── mcp_client.py               # McpClient(token, language) - wrapper httpx para MCP tools (nuevo)
├── infrastructure/
│   └── web/
│       ├── routes/
│       │   ├── route.py                 # Route (entidades) - existente
│       │   ├── route_business.py        # RouteBusiness (auth, geography) - existente
│       │   ├── route_websockets.py      # RouteWebsockets - existente
│       │   └── route_mcp.py             # RouteMcp (nuevo)
│       └── mcp_routes/
│           ├── __init__.py
│           └── business/                # /mcp/business → Chat Service
│               ├── __init__.py
│               ├── server.py            # Instancia FastMCP("goluti-platform-business")
│               └── tools/
│                   ├── __init__.py
│                   ├── auth_tools.py    # 13 tools
│                   └── geography_tools.py # 7 tools
```

Preparado para multiples MCP servers:

```
src/infrastructure/web/mcp_routes/
├── business/                    # /mcp/business → Chat Service
│   ├── server.py
│   └── tools/
├── admin/                       # /mcp/admin → futuro
│   ├── server.py
│   └── tools/
```

Total: 8 archivos nuevos (incluye `tools/__init__.py`). Modificados: `main.py` (2 lineas), `pipfiles.txt` (1 linea), `src/core/config.py` (1 linea).

---

## Implementacion

### 1. Dependencias

Agregar a `pipfiles.txt`:

```
mcp[cli]>=1.2.0
httpx==0.27.2
```

Nota: `httpx` ya esta en `pipfiles.txt`, solo se agrega `mcp[cli]`.

### 2. Route MCP

```python
# src/infrastructure/web/routes/route_mcp.py
from src.infrastructure.web.mcp_routes.business.server import mcp as mcp_business
import src.infrastructure.web.mcp_routes.business.tools.auth_tools      # noqa: F401
import src.infrastructure.web.mcp_routes.business.tools.geography_tools  # noqa: F401


class RouteMcp:
    @staticmethod
    def set_routes(app):
        app.mount("/mcp/business", mcp_business.streamable_http_app())
        # Futuro:
        # app.mount("/mcp/admin", mcp_admin.streamable_http_app())
```

### 3. Server MCP

```python
# src/infrastructure/web/mcp_routes/business/server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "goluti-platform-business",
    instructions="Goluti Platform - Autenticacion, usuarios, companias y geografia"
)
```

### 4. MCP Client

Inspirado en el patron `ApiClient` de Appointment (`src/core/classes/api_client.py`), centraliza las llamadas HTTP para que los tools no repitan codigo.

**Headers de Platform:** `language` (requerido) + `Authorization` (Bearer, solo endpoints auth).

Reutiliza `APP_PORT` que ya existe en todos los `.env` (`APP_PORT=8000`).

**Requiere agregar `app_port` a `Settings`** en `src/core/config.py`:

```python
app_port: int = int(os.getenv("APP_PORT", "8000"))
```

```python
# src/core/classes/mcp_client.py
import json
import httpx
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel
from src.core.config import settings

TIMEOUT = 30.0


class McpClient:
    def __init__(self, token: str = None, language: str = "ES"):
        self.base_url = f"http://localhost:{settings.app_port}"
        self.headers = {"language": language}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def _to_dict(self, data: Union[Dict[str, Any], BaseModel]) -> Dict[str, Any]:
        if isinstance(data, BaseModel):
            return data.model_dump(mode="json")
        return data

    def _handle_response(self, response: httpx.Response) -> str:
        if response.status_code >= 400:
            return json.dumps({"error": True, "status": response.status_code, "detail": response.text})
        return response.text

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                f"{self.base_url}{endpoint}", headers=self.headers, params=params
            )
            return self._handle_response(response)

    async def post(self, endpoint: str, data: Optional[Union[Dict[str, Any], BaseModel]] = None) -> str:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            json_data = self._to_dict(data) if data else None
            response = await client.post(
                f"{self.base_url}{endpoint}", headers=self.headers, json=json_data
            )
            return self._handle_response(response)

    async def put(self, endpoint: str, data: Union[Dict[str, Any], BaseModel]) -> str:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            json_data = self._to_dict(data)
            response = await client.put(
                f"{self.base_url}{endpoint}", headers=self.headers, json=json_data
            )
            return self._handle_response(response)

    async def delete(self, endpoint: str) -> str:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.delete(
                f"{self.base_url}{endpoint}", headers=self.headers
            )
            return self._handle_response(response)
```

### Patron Hibrido de Parametros

Los tools MCP usan un enfoque hibrido para recibir parametros, optimizado para que el LLM pueda construir las llamadas facilmente:

| Tipo de modelo | Patron | Ejemplo |
|----------------|--------|---------|
| **Simple** (1-5 campos planos) | Parametros individuales | `get_children(parent_id: str)` |
| **Compuesto** (sub-objetos) | Campos aplanados con prefijo | `create_company(company_name, location_name, admin_email, ...)` |
| **Con listas anidadas** | Params planos + `_json: str` para la lista | `create_user_internal(..., location_rol_json: str)` |
| **Con Pagination** | Wrapper con filtros pre-armados por dominio | `list_users_internal(skip, limit, name_filter, email_filter)` |

Este enfoque evita:
- Anidamiento innecesario (`params.field`) que confunde al LLM
- Exponer `FilterManager` generico que requiere conocer el DSL de filtros
- Parametros incompletos que no coinciden con los modelos reales

### 5. Auth Tools

```python
# src/infrastructure/web/mcp_routes/business/tools/auth_tools.py
from src.infrastructure.web.mcp_routes.business.server import mcp
from src.core.classes.mcp_client import McpClient


@mcp.tool()
async def login(email: str, password: str, language: str = "ES") -> str:
    """Autenticar usuario en la plataforma Goluti. Retorna access_token y refresh_token."""
    client = McpClient(language=language)
    return await client.post("/auth/login", {"email": email, "password": password})


@mcp.tool()
async def logout(token: str, language: str = "ES") -> str:
    """Cerrar sesion del usuario autenticado."""
    client = McpClient(token=token, language=language)
    return await client.post("/auth/logout")


@mcp.tool()
async def refresh_token(token: str, language: str = "ES") -> str:
    """Renovar token JWT expirado. Retorna nuevo access_token."""
    client = McpClient(token=token, language=language)
    return await client.post("/auth/refresh_token")


@mcp.tool()
async def create_api_token(token: str, rol_id: str, language: str = "ES") -> str:
    """Generar API token de larga duracion para un rol especifico."""
    client = McpClient(token=token, language=language)
    return await client.post("/auth/create-api-token", {"rol_id": rol_id})


@mcp.tool()
async def create_user_internal(
    token: str,
    email: str,
    password: str,
    identification: str,
    first_name: str,
    last_name: str,
    language_id: str,
    currency_id: str,
    location_rol_json: str,
    phone: str = "",
    token_expiration_minutes: int = 60,
    refresh_token_expiration_minutes: int = 1440,
    language: str = "ES",
) -> str:
    """Crear usuario interno (solo ADMIN).
    location_rol_json: JSON array de objetos con location_id y rol_id.
    Ejemplo: [{"location_id":"uuid","rol_id":"uuid"}]
    """
    import json
    client = McpClient(token=token, language=language)
    return await client.post("/auth/create-user-internal", {
        "email": email,
        "password": password,
        "identification": identification,
        "first_name": first_name,
        "last_name": last_name,
        "language_id": language_id,
        "currency_id": currency_id,
        "location_rol": json.loads(location_rol_json),
        "phone": phone,
        "token_expiration_minutes": token_expiration_minutes,
        "refresh_token_expiration_minutes": refresh_token_expiration_minutes,
    })


@mcp.tool()
async def update_user_internal(
    token: str,
    user_id: str,
    password: str = "",
    email: str = "",
    identification: str = "",
    first_name: str = "",
    last_name: str = "",
    phone: str = "",
    state: bool = None,
    rol_id: str = "",
    language: str = "ES",
) -> str:
    """Actualizar datos de un usuario interno. Solo enviar los campos que se quieran cambiar."""
    client = McpClient(token=token, language=language)
    data = {}
    if password: data["password"] = password
    if email: data["email"] = email
    if identification: data["identification"] = identification
    if first_name: data["first_name"] = first_name
    if last_name: data["last_name"] = last_name
    if phone: data["phone"] = phone
    if state is not None: data["state"] = state
    if rol_id: data["rol_id"] = rol_id
    return await client.put(f"/auth/update-user-internal/{user_id}", data)


@mcp.tool()
async def delete_user_internal(token: str, user_id: str, language: str = "ES") -> str:
    """Eliminar usuario interno. Solo ADMIN."""
    client = McpClient(token=token, language=language)
    return await client.delete(f"/auth/delete-user-internal/{user_id}")


@mcp.tool()
async def create_user_external(
    email: str,
    password: str,
    identification: str,
    first_name: str,
    last_name: str,
    language_id: str,
    currency_id: str,
    country_id: str = "",
    phone: str = "",
    token_expiration_minutes: int = 60,
    refresh_token_expiration_minutes: int = 1440,
    language: str = "ES",
) -> str:
    """Registrar usuario externo (auto-registro). No requiere autenticacion."""
    client = McpClient(language=language)
    data = {
        "email": email,
        "password": password,
        "identification": identification,
        "first_name": first_name,
        "last_name": last_name,
        "language_id": language_id,
        "currency_id": currency_id,
        "token_expiration_minutes": token_expiration_minutes,
        "refresh_token_expiration_minutes": refresh_token_expiration_minutes,
    }
    if country_id: data["country_id"] = country_id
    if phone: data["phone"] = phone
    return await client.post("/auth/create-user-external", data)


@mcp.tool()
async def delete_user_external(token: str, user_id: str, language: str = "ES") -> str:
    """Eliminar usuario externo."""
    client = McpClient(token=token, language=language)
    return await client.delete(f"/auth/delete-user-external/{user_id}")


@mcp.tool()
async def list_users_internal(
    token: str,
    skip: int = 0,
    limit: int = 10,
    name_filter: str = "",
    email_filter: str = "",
    language: str = "ES",
) -> str:
    """Listar usuarios internos con paginacion y filtros opcionales."""
    client = McpClient(token=token, language=language)
    filters = []
    if name_filter:
        filters.append({"field": "first_name", "condition": "like", "value": name_filter})
    if email_filter:
        filters.append({"field": "email", "condition": "like", "value": email_filter})
    return await client.post("/auth/users-internal", {
        "skip": skip, "limit": limit, "filters": filters or None
    })


@mcp.tool()
async def list_users_external(
    token: str,
    skip: int = 0,
    limit: int = 10,
    name_filter: str = "",
    email_filter: str = "",
    language: str = "ES",
) -> str:
    """Listar usuarios externos con paginacion y filtros opcionales."""
    client = McpClient(token=token, language=language)
    filters = []
    if name_filter:
        filters.append({"field": "first_name", "condition": "like", "value": name_filter})
    if email_filter:
        filters.append({"field": "email", "condition": "like", "value": email_filter})
    return await client.post("/auth/users-external", {
        "skip": skip, "limit": limit, "filters": filters or None
    })


@mcp.tool()
async def create_company(
    company_name: str,
    company_nit: str,
    location_name: str,
    location_address: str,
    location_phone: str,
    location_email: str,
    location_country_id: str,
    admin_email: str,
    admin_password: str,
    admin_first_name: str,
    admin_last_name: str,
    admin_identification: str,
    admin_phone: str,
    admin_language_id: str,
    admin_currency_id: str,
    admin_rol_id: str,
    company_inactivity_time: int = 30,
    location_city_id: str = "",
    location_latitude: str = "",
    location_longitude: str = "",
    location_google_place_id: str = "",
    language: str = "ES",
) -> str:
    """Crear compania completa con ubicacion y usuario administrador."""
    client = McpClient(language=language)
    company = {"name": company_name, "nit": company_nit, "inactivity_time": company_inactivity_time}
    location = {
        "country_id": location_country_id,
        "name": location_name,
        "address": location_address,
        "phone": location_phone,
        "email": location_email,
    }
    if location_city_id: location["city_id"] = location_city_id
    if location_latitude: location["latitude"] = location_latitude
    if location_longitude: location["longitude"] = location_longitude
    if location_google_place_id: location["google_place_id"] = location_google_place_id
    admin_user = {
        "email": admin_email,
        "password": admin_password,
        "first_name": admin_first_name,
        "last_name": admin_last_name,
        "identification": admin_identification,
        "phone": admin_phone,
        "language_id": admin_language_id,
        "currency_id": admin_currency_id,
        "rol_id": admin_rol_id,
    }
    return await client.post("/auth/create-company", {
        "company": company, "location": location, "admin_user": admin_user
    })


@mcp.tool()
async def delete_company(token: str, company_id: str, language: str = "ES") -> str:
    """Eliminar compania y todos sus datos asociados. ACCION DESTRUCTIVA."""
    client = McpClient(token=token, language=language)
    return await client.delete(f"/auth/delete-company/{company_id}")
```

### 6. Geography Tools

```python
# src/infrastructure/web/mcp_routes/business/tools/geography_tools.py
from src.infrastructure.web.mcp_routes.business.server import mcp
from src.core.classes.mcp_client import McpClient


@mcp.tool()
async def get_countries(language: str = "ES") -> str:
    """Listar todos los paises disponibles en la plataforma."""
    client = McpClient(language=language)
    return await client.get("/geography/countries")


@mcp.tool()
async def get_types_by_country(country_id: str, language: str = "ES") -> str:
    """Obtener tipos de division geografica de un pais (DEPARTMENT, CITY, COMMUNE, etc)."""
    client = McpClient(language=language)
    return await client.post("/geography/country/types", {"country_id": country_id})


@mcp.tool()
async def get_divisions_by_country_type(country_id: str, type_name: str, language: str = "ES") -> str:
    """Obtener todas las divisiones de un pais filtradas por tipo. Ej: todas las ciudades de Colombia."""
    client = McpClient(language=language)
    return await client.post("/geography/country/type", {"country_id": country_id, "type_name": type_name})


@mcp.tool()
async def get_children(parent_id: str, language: str = "ES") -> str:
    """Obtener hijos directos de una division geografica. Ej: ciudades de un departamento."""
    client = McpClient(language=language)
    return await client.post("/geography/children", {"parent_id": parent_id})


@mcp.tool()
async def get_children_by_type(parent_id: str, type_name: str, language: str = "ES") -> str:
    """Obtener descendientes recursivos por tipo. Busca en toda la jerarquia descendente."""
    client = McpClient(language=language)
    return await client.post("/geography/children/type", {"parent_id": parent_id, "type_name": type_name})


@mcp.tool()
async def get_hierarchy(node_id: str, language: str = "ES") -> str:
    """Obtener cadena de ancestros de una division. Ej: Colombia > Antioquia > Medellin."""
    client = McpClient(language=language)
    return await client.post("/geography/hierarchy", {"node_id": node_id})


@mcp.tool()
async def get_division_detail(node_id: str, language: str = "ES") -> str:
    """Obtener detalle completo de una division geografica por ID."""
    client = McpClient(language=language)
    return await client.post("/geography/detail", {"node_id": node_id})
```

### 7. Montaje en main.py

```python
from src.infrastructure.web.routes.route_mcp import RouteMcp

# Existentes:
RouteBusiness.set_routes(app)
Route.set_routes(app)
RouteWebsockets.set_routes(app)

# Nuevo:
RouteMcp.set_routes(app)
```

---

## Pruebas

### Manuales

#### MCP Inspector

```bash
mcp dev src/infrastructure/web/mcp_routes/business/server.py
```

Abre un inspector web para probar tools manualmente.

#### Desde Claude Desktop

En `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "goluti-platform": {
      "url": "http://localhost:8000/mcp/business"
    }
  }
}
```

### Automatizadas

Tests unitarios que validen el correcto funcionamiento del McpClient y los tools:

- **McpClient**: Mockear `httpx.AsyncClient` y verificar que cada metodo construye la URL, headers y body correctamente. Verificar que errores HTTP retornan el formato `{"error": true, "status": ..., "detail": ...}`.
- **Tools**: Mockear `McpClient` y verificar que cada tool llama al endpoint correcto con los parametros correctos.
- **Smoke test**: Verificar que `/mcp/business` responde con la lista de 20 tools.

---

## Despliegue

El endpoint `/mcp/business` se despliega junto con la app existente en Elastic Beanstalk:

```bash
eb deploy platform-env
```

Queda disponible en:
```
http://platform-env.us-east-1.elasticbeanstalk.com/mcp/business
```

Convive con todos los endpoints REST existentes sin interferir.

---

## Plan de Ejecucion

| Paso | Tarea | Archivos |
|------|-------|----------|
| Paso | Tarea | Archivos | Estado |
|------|-------|----------|--------|
| 1 | Agregar dependencia `mcp[cli]>=1.2.0` | `pipfiles.txt` | ✅ |
| 2 | Agregar `app_port` a `Settings` (reutiliza `APP_PORT` de `.env`) | `src/core/config.py` | ✅ |
| 3 | Crear `mcp_client.py` con clase McpClient | `src/core/classes/mcp_client.py` | ✅ |
| 4 | Crear `route_mcp.py` con `RouteMcp.set_routes` | `src/.../routes/route_mcp.py` | ✅ |
| 5 | Crear `server.py` con instancia FastMCP | `src/.../mcp_routes/business/server.py` | ✅ |
| 6 | Implementar `auth_tools.py` (13 tools) | `src/.../mcp_routes/business/tools/auth_tools.py` | ✅ |
| 7 | Implementar `geography_tools.py` (7 tools) | `src/.../mcp_routes/business/tools/geography_tools.py` | ✅ |
| 8 | Agregar `RouteMcp.set_routes(app)` en main.py | `main.py` | ✅ |
| 9 | Instalar `mcp[cli]` en virtualenv | `pip install` | Pendiente por entorno |
| 10 | Implementar tests automatizados | `tests/` | Pendiente |
| 11 | Probar con `mcp dev` | - | Pendiente |
| 12 | Desplegar en Elastic Beanstalk | `eb deploy` | Pendiente |

### Notas de implementacion

- **FastMCP 1.26**: Usa `instructions=` en vez de `description=` en el constructor
- **`tools/__init__.py`**: Necesario para completar el package (8 archivos nuevos en total)
- **Verificado**: 20 tools registrados, app carga con `/mcp/business` montado como `Mount`

---

## Riesgos

| Riesgo | Impacto | Mitigacion |
|--------|---------|------------|
| `delete_company` invocado por AI sin confirmacion | Alto | Descripcion del tool indica "ACCION DESTRUCTIVA"; Chat Service debe pedir confirmacion |
| Token JWT expira entre llamadas MCP | Medio | El cliente MCP debe manejar refresh_token |
| Token JWT visible en contexto del LLM | Medio | El token se pasa como parametro del tool (el LLM lo "ve"). En futuro evaluar extraerlo del header de sesion MCP para evitar exposicion en logs |
| Middlewares no se propagan a sub-app montada | Bajo | El MCP solo hace loopback HTTP a endpoints REST que si tienen middlewares. El MCP no es consumido por frontend |
| Latencia extra por HTTP loopback | Bajo | localhost es ~0.1ms; despreciable. Cada tool crea un `AsyncClient` efimero por simplicidad |
| Dependencia `mcp` conflicta con paquetes existentes | Bajo | Probar en entorno local antes de desplegar |

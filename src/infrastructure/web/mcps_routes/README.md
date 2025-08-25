# MCP (Model Context Protocol) Service

Este servicio actúa como un proxy hacia el API externo de la plataforma backend. Permite que esta aplicación se comunique con el servicio externo de manera transparente.

## Configuración

El servicio MCP se puede configurar usando variables de entorno:

### Variables de Entorno

- `MCP_BASE_URL`: URL base del servicio externo (por defecto: `http://backend-platform-prod-env.eba-dddmvypu.us-east-1.elasticbeanstalk.com`)
- `MCP_TIMEOUT`: Timeout para las requests en segundos (por defecto: `30.0`)
- `MCP_VERIFY_SSL`: Verificar certificados SSL (por defecto: `true`)
- `MCP_API_KEY`: Clave API opcional si el servicio externo la requiere
- `MCP_MAX_RETRIES`: Número máximo de reintentos (por defecto: `3`)
- `MCP_RETRY_DELAY`: Delay entre reintentos en segundos (por defecto: `1.0`)

### Ejemplo de configuración .env

```bash
MCP_BASE_URL=http://backend-platform-prod-env.eba-dddmvypu.us-east-1.elasticbeanstalk.com
MCP_TIMEOUT=30.0
MCP_VERIFY_SSL=true
MCP_API_KEY=your_api_key_here
MCP_MAX_RETRIES=3
MCP_RETRY_DELAY=1.0
```

## Endpoints Disponibles

El servicio MCP expone los siguientes grupos de endpoints bajo el prefijo `/mcp`:

### Autenticación
- `POST /mcp/auth/login` - Login
- `POST /mcp/auth/refresh_token` - Refresh token
- `POST /mcp/auth/logout` - Logout
- `POST /mcp/auth/create-api-token` - Crear API token

### API Tokens
- `POST /mcp/api-token` - Crear API token
- `PUT /mcp/api-token` - Actualizar API token
- `POST /mcp/api-token/list` - Listar API tokens
- `DELETE /mcp/api-token/{id}` - Eliminar API token
- `GET /mcp/api-token/{id}` - Obtener API token

### Currency Location
- `POST /mcp/currency-location` - Crear currency location
- `PUT /mcp/currency-location` - Actualizar currency location
- `POST /mcp/currency-location/list` - Listar currency locations
- `DELETE /mcp/currency-location/{id}` - Eliminar currency location
- `GET /mcp/currency-location/{id}` - Obtener currency location

### Users
- `POST /mcp/user` - Crear usuario
- `PUT /mcp/user` - Actualizar usuario
- `POST /mcp/user/list` - Listar usuarios
- `DELETE /mcp/user/{id}` - Eliminar usuario
- `GET /mcp/user/{id}` - Obtener usuario

## Headers Requeridos

Todos los endpoints requieren el header `language` y la mayoría requieren autorización:

```bash
language: es  # Idioma
Authorization: Bearer <token>  # Token de autorización (excepto login)
```

## Uso

### Ejemplo de Login

```bash
curl -X POST "http://localhost:8000/mcp/auth/login" \
  -H "language: es" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Ejemplo de Listado de Usuarios

```bash
curl -X POST "http://localhost:8000/mcp/user/list" \
  -H "language: es" \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "page": 1,
    "limit": 10
  }'
```

## Manejo de Errores

El servicio MCP maneja automáticamente los errores del servicio externo y devuelve respuestas estructuradas:

```json
{
  "error": true,
  "status_code": 400,
  "message": "External API error: Invalid request",
  "details": "Detailed error information"
}
```

## Arquitectura

El servicio está compuesto por:

1. **Router** (`mcp_router.py`): Define todos los endpoints
2. **Controller** (`mcp_controller.py`): Maneja la lógica de negocio y comunicación con el API externo
3. **Config** (`config.py`): Configuración del servicio
4. **Routes** (`route_mcps.py`): Configuración de rutas para FastAPI

## Extensibilidad

Para agregar nuevos endpoints:

1. Agregar el endpoint en `mcp_router.py`
2. Implementar el método correspondiente en `mcp_controller.py`
3. Los endpoints seguirán automáticamente el patrón de proxy al servicio externo

## Monitoreo

El servicio incluye:

- Manejo de timeouts configurables
- Retry logic (configurable)
- Logging de errores
- Respuestas estructuradas para debugging

# Flujos de Desarrollo - Overview

**Versión**: 1.6  
**Fecha**: Noviembre 11, 2024  
**Estado**: Vigente  
**Autor(es)**: Equipo de Desarrollo Goluti

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Propósito de esta Carpeta](#propósito-de-esta-carpeta)
3. [Tipos de Documentación de Flujos](#tipos-de-documentación-de-flujos)
4. [Nomenclatura de Documentos](#nomenclatura-de-documentos)
5. [Plantilla para Nuevos Flujos](#plantilla-para-nuevos-flujos)
6. [Ejemplos de Flujos](#ejemplos-de-flujos)
7. [Ciclo de Vida de Documentación](#ciclo-de-vida-de-documentación)
8. [Referencias](#referencias)

---

## Introducción

Esta carpeta contiene la documentación de **nuevos flujos de desarrollo** que están siendo implementados en el sistema. A diferencia de Entity Flow y Business Flow que son patrones establecidos, esta sección documenta features, módulos o flujos específicos en desarrollo.

---

## Propósito de esta Carpeta

### ¿Qué Documenta?

Esta carpeta documenta:

- **Nuevos módulos de negocio** en desarrollo
- **Features complejas** que involucran múltiples componentes
- **Flujos específicos** que no encajan en Entity o Business Flow estándar
- **Integraciones** con sistemas externos
- **Procesos especiales** del dominio de negocio

### ¿Qué NO Documenta?

No documenta:
- Entidades CRUD estándar → usar Entity Flow
- Lógica de negocio estándar → usar Business Flow
- Componentes core → usar Core Components
- Arquitectura general → usar Architecture

---

## Tipos de Documentación de Flujos

### 1. **Flujos de Proceso de Negocio**

Procesos específicos del dominio que involucran múltiples pasos.

**Ejemplos:**
- Flujo de onboarding de clientes
- Flujo de aprobación de documentos
- Flujo de procesamiento de pagos
- Flujo de gestión de inventario

**Contenido típico:**
- Descripción del proceso
- Actores involucrados
- Estados del proceso
- Transiciones entre estados
- Validaciones y reglas de negocio
- Diagramas de flujo
- Endpoints HTTP
- Ejemplos de uso

### 2. **Flujos de Integración**

Integraciones con sistemas externos o APIs de terceros.

**Ejemplos:**
- Integración con pasarela de pagos
- Integración con servicio de mensajería (SMS, Email)
- Integración con proveedores de KYC/AML
- Integración con sistemas contables
- Webhooks externos

**Contenido típico:**
- Sistema externo
- Propósito de la integración
- Autenticación y seguridad
- Endpoints consumidos
- Formato de datos
- Manejo de errores
- Reintentos y timeouts
- Logs y monitoreo

### 3. **Flujos de Features Complejas**

Features que requieren múltiples componentes y coordinación.

**Ejemplos:**
- Sistema de notificaciones multi-canal
- Motor de reportes dinámicos
- Sistema de permisos granulares
- Auditoría y trazabilidad completa
- Búsqueda avanzada con Elasticsearch

**Contenido típico:**
- Objetivo de la feature
- Arquitectura de la feature
- Componentes involucrados
- Base de datos (tablas nuevas)
- APIs expuestas
- Configuración
- Casos de uso
- Pruebas

### 4. **Flujos de Migración**

Procesos de migración de datos o transformación de sistemas.

**Ejemplos:**
- Migración de sistema legacy
- Transformación de estructura de datos
- Importación masiva de datos
- Sincronización de sistemas

**Contenido típico:**
- Origen y destino
- Mapeo de datos
- Scripts de migración
- Validaciones
- Rollback
- Timeline

---

## Nomenclatura de Documentos

### Patrón de Nombres

```
07-{secuencia}-{nombre-descriptivo-del-flujo}.md
```

**Ejemplos:**
- `07-01-onboarding-flow.md`
- `07-02-payment-integration-flow.md`
- `07-03-notification-system-flow.md`
- `07-04-document-approval-flow.md`

### Reglas de Nomenclatura

1. **Secuencia numérica**: `01`, `02`, `03`, etc.
2. **Nombre descriptivo**: Describe claramente el flujo
3. **Separadores**: Usar guiones `-`
4. **Minúsculas**: Todo en minúsculas
5. **Sin espacios**: Usar guiones en lugar de espacios

---

## Plantilla para Nuevos Flujos

### Estructura Recomendada

```markdown
# Nombre del Flujo

**Versión**: 1.0  
**Fecha**: [Fecha]  
**Estado**: [Desarrollo | En Revisión | Implementado | Deprecado]  
**Autor(es)**: [Nombres]  
**Responsable**: [Nombre del líder técnico]

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Objetivo](#objetivo)
3. [Contexto de Negocio](#contexto-de-negocio)
4. [Actores Involucrados](#actores-involucrados)
5. [Diagrama de Flujo](#diagrama-de-flujo)
6. [Especificación Técnica](#especificación-técnica)
7. [Endpoints API](#endpoints-api)
8. [Modelos de Datos](#modelos-de-datos)
9. [Base de Datos](#base-de-datos)
10. [Validaciones y Reglas](#validaciones-y-reglas)
11. [Manejo de Errores](#manejo-de-errores)
12. [Seguridad](#seguridad)
13. [Ejemplos de Uso](#ejemplos-de-uso)
14. [Testing](#testing)
15. [Referencias](#referencias)
16. [Historial de Cambios](#historial-de-cambios)

---

## Introducción

[Descripción breve del flujo, qué problema resuelve]

---

## Objetivo

[Objetivo específico de este flujo]

### Alcance

**En alcance:**
- [Item 1]
- [Item 2]

**Fuera de alcance:**
- [Item 1]
- [Item 2]

---

## Contexto de Negocio

[Explicación del contexto de negocio, por qué es necesario este flujo]

### Problema que Resuelve

[Descripción del problema]

### Beneficios Esperados

- [Beneficio 1]
- [Beneficio 2]

---

## Actores Involucrados

| Actor | Rol | Responsabilidad |
|-------|-----|-----------------|
| **Usuario Final** | Usuario del sistema | Iniciar el proceso |
| **Administrador** | Admin | Aprobar/rechazar |
| **Sistema** | Automático | Validar y procesar |

---

## Diagrama de Flujo

```
[Diagrama en ASCII o descripción del flujo]

Ejemplo:
┌─────────┐     ┌──────────┐     ┌───────────┐     ┌─────────┐
│ Inicio  │────▶│ Validar  │────▶│ Procesar  │────▶│  Fin    │
└─────────┘     └──────────┘     └───────────┘     └─────────┘
```

### Estados del Flujo

| Estado | Descripción | Transiciones Posibles |
|--------|-------------|----------------------|
| **PENDING** | Solicitud pendiente | → PROCESSING, REJECTED |
| **PROCESSING** | En procesamiento | → COMPLETED, FAILED |
| **COMPLETED** | Completado exitosamente | - |
| **FAILED** | Falló el proceso | → PENDING (retry) |
| **REJECTED** | Rechazado | - |

---

## Especificación Técnica

### Arquitectura

[Diagrama de componentes involucrados]

### Componentes Principales

#### 1. [Nombre del Componente]

**Ubicación**: `src/domain/services/use_cases/...`

**Responsabilidad**: [Descripción]

**Dependencias**:
- [Dependencia 1]
- [Dependencia 2]

---

## Endpoints API

### Endpoint 1: [Nombre del Endpoint]

```
POST /api/v1/flow/endpoint
```

**Headers:**
```
Authorization: Bearer <token>
Language: es | en
Content-Type: application/json
```

**Request Body:**
```json
{
  "field1": "value1",
  "field2": "value2"
}
```

**Response (Success):**
```json
{
  "message_type": "temporary",
  "notification_type": "success",
  "message": "Operación exitosa",
  "response": {
    "id": "uuid",
    "status": "PROCESSING"
  }
}
```

**Códigos de Estado:**
- **200 OK**: Operación exitosa
- **400 Bad Request**: Parámetros inválidos
- **403 Forbidden**: Sin permisos
- **500 Internal Server Error**: Error del servidor

---

## Modelos de Datos

### Request Models

```python
class FlowRequest(BaseModel):
    field1: str
    field2: int
    field3: Optional[str] = None
```

### Response Models

```python
class FlowResponse(BaseModel):
    id: UUID4
    status: str
    created_date: datetime
```

---

## Base de Datos

### Nuevas Tablas

#### Tabla: `flow_table`

```sql
CREATE TABLE platform.flow_table (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES platform.user(id),
    status VARCHAR(50) NOT NULL,
    data JSONB,
    created_date TIMESTAMP DEFAULT NOW(),
    updated_date TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES platform.user(id)
);
```

### Migraciones

**Archivo**: `migrations/changelog-vXX.sql`

---

## Validaciones y Reglas

### Reglas de Negocio

1. **Regla 1**: [Descripción]
2. **Regla 2**: [Descripción]

### Validaciones Técnicas

- Campo X debe ser mayor que 0
- Campo Y es obligatorio
- Campo Z debe tener formato email

---

## Manejo de Errores

| Error | Código | Mensaje | Solución |
|-------|--------|---------|----------|
| Campo inválido | 400 | "Campo X es inválido" | Verificar formato |
| Sin permisos | 403 | "No tiene permisos" | Solicitar acceso |

---

## Seguridad

### Permisos Requeridos

- `PERMISSION_TYPE.FLOW_EXECUTE`
- `PERMISSION_TYPE.FLOW_APPROVE` (para aprobadores)

### Validaciones de Seguridad

- Validación de token JWT
- Verificación de permisos por rol
- Rate limiting: 100 requests/hora

---

## Ejemplos de Uso

### Caso de Uso 1: [Nombre]

[Descripción del caso de uso]

**Request:**
```bash
curl -X POST https://api.goluti.com/api/v1/flow/endpoint \
  -H "Authorization: Bearer TOKEN" \
  -H "Language: es" \
  -d '{"field1": "value1"}'
```

**Response:**
```json
{...}
```

---

## Testing

### Unit Tests

```python
async def test_flow_success():
    # Test implementation
    pass

async def test_flow_validation_error():
    # Test implementation
    pass
```

### Integration Tests

[Descripción de pruebas de integración]

---

## Referencias

- **[Documento relacionado 1]**: Descripción
- **[Documento relacionado 2]**: Descripción

---

## Historial de Cambios

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0 | [Fecha] | Creación inicial | [Autor] |

---

**Fin del Documento**
```

---

## Ejemplos de Flujos

### Flujo Implementado 1: Create User Internal ✅

**Archivo**: `07-01-create-user-internal-flow.md`

**Estado**: Especificado (Versión 1.1)

**Contenido**:
- Creación de usuario interno completo
- Validaciones de referencias (language, currency)
- Validación de lista `location_rol` con múltiples asignaciones
- Validación de combinaciones únicas (location_id, rol_id)
- Creación de Platform
- Creación de User con hash de password
- **Asignación múltiple de roles por ubicación** (UserLocationRol)
- Soporte para múltiples ubicaciones con diferentes roles
- Soporte para misma ubicación con múltiples roles
- Respuesta completa con todas las asignaciones

**Características Destacadas**:
- **Flexibilidad**: Un usuario puede tener diferentes roles en diferentes ubicaciones
- **Multi-rol**: Un usuario puede tener múltiples roles en la misma ubicación
- **Atomicidad**: Rollback completo si falla cualquier asignación

**Use Cases Involucrados**:
- Validación: LanguageReadUseCase, LocationReadUseCase (N veces), CurrencyReadUseCase, RolReadUseCase (N veces), UserListUseCase
- Creación: PlatformSaveUseCase, UserSaveUseCase, UserLocationRolSaveUseCase (N veces)

**Endpoint**: `POST /auth/create-user-internal`

**Ejemplo de Request**:
```json
{
  "location_rol": [
    {"location_id": "loc-1", "rol_id": "admin"},
    {"location_id": "loc-2", "rol_id": "operator"},
    {"location_id": "loc-1", "rol_id": "auditor"}
  ],
  ...
}
```

---

### Flujo Implementado 2: Create User External ✅

**Archivo**: `07-02-create-user-external-flow.md`

**Estado**: Especificado (Versión 1.0)

**Contenido**:
- Creación de usuario externo (público) sin roles corporativos
- Validaciones de referencias (language, currency)
- Validación de unicidad de email
- Validación de unicidad de identification
- Creación de Platform **sin ubicación** (`location_id = null`)
- Creación de User con hash de password
- **Sin asignación de roles** (usuarios públicos)
- Endpoint público (sin autenticación requerida)

**Características Destacadas**:
- **Simplicidad**: No requiere información corporativa
- **Público**: Endpoint sin autenticación para registro abierto
- **Flexible**: Platform sin ubicación permite uso global
- **Seguro**: Validaciones estrictas de unicidad (email + identification)

**Use Cases Involucrados**:
- Validación: LanguageReadUseCase, CurrencyReadUseCase, UserListUseCase (email), UserListUseCase (identification)
- Creación: PlatformSaveUseCase, UserSaveUseCase

**Endpoint**: `POST /auth/create-user-external`

**Ejemplo de Request**:
```json
{
  "language_id": "550e8400-e29b-41d4-a716-446655440000",
  "currency_id": "770e8400-e29b-41d4-a716-446655440000",
  "email": "usuario@example.com",
  "password": "SecurePassword123!",
  "identification": "12345678",
  "first_name": "Juan",
  "last_name": "Pérez",
  "phone": "+573001234567"
}
```

---

### Flujo Implementado 3: List Users by Location ✅

**Archivo**: `07-03-list-users-by-location-flow.md`

**Estado**: Especificado (Versión 1.0)

**Contenido**:
- **Usa directamente clase `Pagination` del core** (no crea request personalizado - reutilización)
- Query con JOINs entre `user_location_rol`, `user` y `rol`
- **⚡ Optimización de paginación dual**:
  - Sin filtros → Paginación en SQL (`offset/limit`) - más eficiente
  - Con filtros → Paginación en memoria (después de filtrar)
- Sistema de filtros **flexible y genérico** usando `filters` de `Pagination`
- **El desarrollador puede filtrar por CUALQUIER campo del response** (`UserByLocationItem`)
- `location_id` es **opcional**, se filtra mediante `filters` si se necesita
- Todos los 15 campos retornados son filtrables: UUIDs, strings, boolean, fechas
- Retorna información completa del usuario (sin password) + rol
- **Un usuario tiene UN SOLO rol por ubicación** (constraint único)
- Requiere autenticación y permiso READ

**Características Destacadas**:
- **Reutilización de Código**: Usa directamente `Pagination` del core sin crear modelo personalizado
- **⚡ Optimización Dual**: Paginación en SQL (sin filtros) o en memoria (con filtros) según el caso
- **Flexibilidad Total**: El desarrollador puede filtrar por cualquier campo sin restricciones
- **Performance**: Query optimizado con JOINs directos + paginación inteligente
- **Seguridad**: Password nunca se expone
- **Patrón Consistente**: Usa `apply_memory_filters` y `build_alias_map` (patrón del proyecto)
- **Escalabilidad**: Paginación adaptativa para grandes volúmenes

**Tecnología**:
- SQLAlchemy con JOINs directos (sin N+1 queries)
- **Paginación dual adaptativa**:
  - Sin filtros → `stmt.offset().limit()` en SQL (óptimo)
  - Con filtros → Paginación en memoria después de filtrar
- Filtros usando `apply_memory_filters` y `build_alias_map`

**Endpoint**: `POST /auth/users-internal`

**Ejemplo de Request 1 - Por ubicación (paginado)**:
```json
{
  "skip": 0,
  "limit": 10,
  "filters": [
    {
      "field": "location_id",
      "condition": "equals",
      "value": "660e8400-e29b-41d4-a716-446655440000"
    }
  ]
}
```

**Ejemplo de Request 2 - Todos los ADMIN del sistema**:
```json
{
  "all_data": true,
  "filters": [
    {
      "field": "rol_code",
      "condition": "equals",
      "value": "ADMIN"
    }
  ]
}
```

**Ejemplo de Response**:
```json
{
  "response": [
    {
      "user_location_rol_id": "uuid-1",
      "location_id": "location-uuid",
      "user_id": "user-uuid-1",
      "email": "juan@goluti.com",
      "first_name": "Juan",
      "last_name": "Pérez",
      "rol_id": "rol-uuid-1",
      "rol_name": "Administrador",
      "rol_code": "ADMIN"
    },
    {
      "user_location_rol_id": "uuid-2",
      "location_id": "location-uuid",
      "user_id": "user-uuid-2",
      "email": "maria@goluti.com",
      "first_name": "María",
      "last_name": "López",
      "rol_id": "rol-uuid-2",
      "rol_name": "Operador",
      "rol_code": "OPERATOR"
    }
  ]
}
```

---

### Flujo Implementado 4: List Users External ✅

**Archivo**: `07-04-list-users-external-flow.md`

**Estado**: Especificado (Versión 2.2)

**Contenido**:
- **Usa directamente clase `Pagination` del core** (no crea request personalizado - reutilización)
- **⚠️ Cambio fundamental**: Los usuarios externos **NO tienen registro en `user_location_rol` ni `rol`**
- Se registran **SOLO** en las tablas `user` y `platform`
- **Query con doble validación de seguridad**:
  - INNER JOIN entre `user` y `platform`
  - LEFT JOIN con `user_location_rol` para validar que NO existe registro
- **🔒 Doble filtro de seguridad**:
  - **Filtro 1**: `platform.location_id IS NULL` (identificador principal)
  - **Filtro 2**: `user_location_rol.id IS NULL` (validación adicional mediante LEFT JOIN)
- Esta doble capa previene casos edge y garantiza separación absoluta usuarios internos/externos
- **⚡ Optimización de paginación dual**:
  - Sin filtros → Paginación en SQL (`offset/limit`) - más eficiente
  - Con filtros → Paginación en memoria (después de filtrar)
- Sistema de filtros **flexible y genérico** usando `filters` de `Pagination`
- **El desarrollador puede filtrar por CUALQUIER campo del response** (`UserExternalItem`)
- Todos los **16 campos** retornados son filtrables (campos de `user` + `platform`)
- Retorna información completa del usuario + platform (sin password)
- **Nota**: `platform_state` removido (no existe en `PlatformEntity`)
- Requiere autenticación y permiso READ

**Características Destacadas**:
- **🔒 Seguridad Robusta**: Doble validación SQL para garantizar solo usuarios externos
- **Reutilización de Código**: Usa directamente `Pagination` del core sin crear modelo personalizado
- **⚡ Optimización Dual**: Paginación en SQL (sin filtros) o en memoria (con filtros) según el caso
- **Flexibilidad Total**: El desarrollador puede filtrar por cualquier campo sin restricciones
- **Performance**: Query optimizado con 1 INNER JOIN + 1 LEFT JOIN (sin N+1 queries)
- **Prevención de Casos Edge**: Imposible mezclar usuarios internos con externos
- **Patrón Consistente**: Usa `apply_memory_filters` y `build_alias_map` (patrón del proyecto)
- **Escalabilidad**: Paginación adaptativa para grandes volúmenes

**Tecnología**:
- SQLAlchemy con INNER JOIN (`user` ⟷ `platform`) + LEFT JOIN (`user_location_rol`)
- **Doble validación en SQL**: `platform.location_id IS NULL` AND `user_location_rol.id IS NULL`
- **Paginación dual adaptativa**:
  - Sin filtros → `stmt.offset().limit()` en SQL (óptimo)
  - Con filtros → Paginación en memoria después de filtrar
- Filtros usando `apply_memory_filters` y `build_alias_map`

**Endpoint**: `POST /auth/users-external`

**Ejemplo de Request 1 - Buscar por email (paginado)**:
```json
{
  "skip": 0,
  "limit": 10,
  "filters": [
    {
      "field": "email",
      "condition": "like",
      "value": "@gmail.com"
    }
  ]
}
```

**Ejemplo de Request 2 - Filtrar por configuración de token**:
```json
{
  "skip": 0,
  "limit": 10,
  "filters": [
    {
      "field": "token_expiration_minutes",
      "condition": "gte",
      "value": 60
    }
  ]
}
```

**Ejemplo de Response**:
```json
{
  "response": [
    {
      "platform_id": "platform-uuid-1",
      "user_id": "user-uuid-1",
      "email": "carlos@gmail.com",
      "identification": "98765432",
      "first_name": "Carlos",
      "last_name": "Ramírez",
      "phone": "+573009876543",
      "user_state": true,
      "user_created_date": "2024-03-20T15:45:00Z",
      "user_updated_date": "2024-03-20T15:45:00Z",
      "language_id": "lang-uuid",
      "currency_id": "currency-uuid",
      "token_expiration_minutes": 60,
      "refresh_token_expiration_minutes": 1440,
      "platform_created_date": "2024-03-20T15:45:00Z",
      "platform_updated_date": "2024-03-20T15:45:00Z"
    },
    {
      "platform_id": "platform-uuid-2",
      "user_id": "user-uuid-2",
      "email": "ana@hotmail.com",
      "identification": "11223344",
      "first_name": "Ana",
      "last_name": "Torres",
      "phone": "+573001122334",
      "user_state": true,
      "user_created_date": "2024-04-10T09:30:00Z",
      "user_updated_date": "2024-04-10T09:30:00Z",
      "language_id": "lang-uuid",
      "currency_id": "currency-uuid",
      "token_expiration_minutes": 60,
      "refresh_token_expiration_minutes": 1440,
      "platform_created_date": "2024-04-10T09:30:00Z",
      "platform_updated_date": "2024-04-10T09:30:00Z"
    }
  ]
}
```

---

### Ejemplo Sugerido 5: Onboarding de Clientes

**Archivo**: `07-05-onboarding-flow.md`

**Contenido**:
- Registro inicial del cliente
- Validación de identidad (KYC)
- Verificación de documentos
- Aprobación manual
- Activación de cuenta
- Notificaciones

### Ejemplo Sugerido 6: Flujo de Pagos

**Archivo**: `07-06-payment-flow.md`

**Contenido**:
- Integración con pasarela de pagos
- Creación de orden de pago
- Procesamiento del pago
- Webhooks de confirmación
- Conciliación bancaria
- Generación de comprobantes

### Ejemplo Sugerido 7: Sistema de Notificaciones

**Archivo**: `07-07-notification-system-flow.md`

**Contenido**:
- Tipos de notificaciones (email, SMS, push)
- Templates de notificaciones
- Cola de procesamiento
- Reintentos y fallbacks
- Tracking de entrega
- Preferencias de usuario

---

## Ciclo de Vida de Documentación

### Estados de un Flujo

```
┌──────────────┐     ┌─────────────┐     ┌──────────────┐     ┌────────────┐
│ Desarrollo   │────▶│ En Revisión │────▶│ Implementado │────▶│ Deprecado  │
└──────────────┘     └─────────────┘     └──────────────┘     └────────────┘
```

### 1. **Desarrollo**

- Flujo en diseño o implementación
- Documento puede estar incompleto
- Se actualiza frecuentemente

### 2. **En Revisión**

- Implementación completada
- Pendiente de revisión de código
- Pendiente de pruebas

### 3. **Implementado**

- Código en producción
- Documento finalizado
- Mantenimiento según necesidad

### 4. **Deprecado**

- Flujo obsoleto o reemplazado
- Mantener para referencia histórica
- Indicar en el estado del documento

### Actualización de Estados

Al cambiar el estado de un flujo:

1. Actualizar campo **Estado** en el header
2. Agregar entrada en **Historial de Cambios**
3. Actualizar fecha de última modificación
4. Si es deprecado, agregar nota con reemplazo

---

## Mejores Prácticas

### ✅ Hacer

- **Documentar temprano**: Crear documento al inicio del desarrollo
- **Mantener actualizado**: Actualizar según avanza la implementación
- **Incluir diagramas**: Visualizar facilita comprensión
- **Ejemplos reales**: Usar casos de uso concretos
- **Referencias**: Enlazar documentos relacionados
- **Control de versiones**: Registrar todos los cambios

### ❌ Evitar

- Documentar después de implementar
- Dejar documentos desactualizados
- Solo texto sin diagramas
- Ejemplos teóricos sin valor
- Documentos aislados sin contexto
- Cambios sin registrar

---

## Integración con Otros Documentos

### Flujos vs Entity Flow

- **Entity Flow**: Patrón CRUD estándar aplicable a todas las entidades
- **Flujos (esta carpeta)**: Procesos específicos que pueden usar múltiples entidades

### Flujos vs Business Flow

- **Business Flow**: Lógica de negocio compleja pero genérica (Auth)
- **Flujos (esta carpeta)**: Lógica de negocio específica del dominio

### Cuándo Usar Cada Uno

| Necesidad | Documentar en |
|-----------|---------------|
| Nueva entidad CRUD | Entity Flow (seguir patrón) |
| Autenticación/Autorización genérica | Business Flow |
| Proceso específico del negocio | **07-flows/** (aquí) |
| Integración externa | **07-flows/** (aquí) |
| Feature compleja multi-componente | **07-flows/** (aquí) |

---

### Flujo Implementado 5: Create Company ✅

**Archivo**: `07-05-create-company-flow.md`

**Estado**: Especificado (Versión 1.0)

**Contenido**:
- **Endpoint PÚBLICO** (sin autenticación) para auto-registro de compañías
- Creación completa de compañía en una sola operación atómica
- Creación de registro de compañía
- **Clonación inteligente de menús** desde plantilla global (menús con `company_id = NULL`)
- **Preservación de jerarquías padre-hijo** en menús clonados:
  - Menús cabeza: `id == top_id` (mantienen esta característica)
  - Menús hijo: `top_id` apunta al padre correcto mapeado
  - Genera nuevos UUIDs usando `uuid.uuid4()` con mapeo bidireccional
- Clonación de permisos de menú desde plantilla
- Creación de ubicación principal (`main_location = true`)
- Creación de usuario administrador inicial usando `CreateUserInternalUseCase`
- Validaciones exhaustivas (NIT único, email único, referencias existen)
- **Transaccionalidad completa**: todo o nada (rollback automático si falla cualquier paso)
- **Medidas de seguridad**: Rate limiting (3/hora), reCAPTCHA, auditoría de intentos

**Características Destacadas**:
- **Público y Accesible**: No requiere autenticación, ideal para onboarding self-service
- **Onboarding Rápido**: Una compañía completa en segundos vs horas manuales
- **Estructura Estándar**: Todas las compañías inician con la misma plantilla de menús
- **Preservación de Relaciones**: Algoritmo de mapeo mantiene jerarquías complejas
- **Atomicidad**: Garantiza consistencia total usando transacciones
- **Reutilización**: Usa `CreateUserInternalUseCase` existente para crear admin
- **Escalabilidad**: Plantilla centralizada fácil de mantener
- **Seguro**: Rate limiting, validaciones estrictas, auditoría de intentos, opcional reCAPTCHA

**Algoritmo de Clonación de Menús**:
1. Consultar menús template (`company_id = NULL`)
2. Primera pasada: generar mapeo `old_id → new_id` para todos los menús
3. Segunda pasada: crear menús preservando relaciones:
   - Si es cabeza (`id == top_id`): `new_top_id = new_id`
   - Si es hijo (`id != top_id`): `new_top_id = mapping[old_top_id]`
4. Asociar todos los menús al nuevo `company_id`

**Use Cases Involucrados**:
- Validación: CompanyListUseCase (NIT), UserListUseCase (email), CountryReadUseCase, LanguageReadUseCase, CurrencyReadUseCase, RolReadUseCase, MenuListUseCase, MenuPermissionListUseCase (N veces)
- Creación: CompanySaveUseCase, MenuSaveUseCase (N veces), MenuPermissionSaveUseCase (M veces), LocationSaveUseCase, CreateUserInternalUseCase

**Endpoint**: `POST /auth/create-company`

**Ejemplo de Request**:
```json
{
  "company": {
    "name": "TechStart S.A.S.",
    "nit": "900555666-1",
    "inactivity_time": 30
  },
  "location": {
    "country_id": "uuid",
    "name": "Sede Principal",
    "address": "Calle 123 #45-67",
    "city": "Bogotá",
    "phone": "+57 300 1234567",
    "email": "info@techstart.com"
  },
  "admin_user": {
    "email": "admin@techstart.com",
    "password": "SecurePassword123!",
    "first_name": "María",
    "last_name": "González",
    "identification_type": "CC",
    "identification_number": "1234567890",
    "phone": "+57 300 1234567",
    "language_id": "uuid",
    "currency_id": "uuid",
    "rol_id": "uuid"
  }
}
```

**Ejemplo de Response**:
```json
{
  "success": true,
  "data": null,
  "message": "Compañía creada exitosamente"
}
```

---

## Referencias

- **[00-00] Documentation Methodology**: Metodología de documentación
- **[02-00] Entity Flow Overview**: Patrón CRUD estándar
- **[03-00] Business Flow Overview**: Lógica de negocio compleja
- **[01-00] Architecture Overview**: Arquitectura general del sistema
- **[07-01] Create User Internal Flow**: Flujo reutilizado para crear usuario admin
- **Changelog v28**: Script para hacer `company_id` opcional en tabla `menu`
- **Changelog v29**: Script para insertar menús globales (plantilla)

---

## Historial de Cambios

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0 | Nov 2024 | Creación inicial de carpeta Flows. Documentación de Flujo 1: Create User Internal | Equipo de Desarrollo Goluti |
| 1.1 | Nov 2024 | Agregado Flujo 2: Create User External. Endpoint público para crear usuarios externos sin roles corporativos. Platform sin ubicación (location_id = null) | Equipo de Desarrollo Goluti |
| 1.2 | Nov 2024 | Agregado Flujo 3: List Users by Location. Endpoint: `/auth/users-internal`. **Usa directamente clase `Pagination` del core** sin crear request personalizado (reutilización de código). **⚡ Optimización de paginación dual**: Sin filtros → Paginación en SQL (`offset/limit`); Con filtros → Paginación en memoria (después de filtrar). Sistema de filtros flexible y genérico - **el desarrollador puede filtrar por CUALQUIER campo del response** (15 campos filtrables). `location_id` es opcional, se filtra mediante `filters`. Query con JOINs. Filtros aplicados en memoria usando `apply_memory_filters` y `build_alias_map`. Password excluido. Regla de negocio: Un usuario tiene UN SOLO rol por ubicación. | Equipo de Desarrollo Goluti |
| 1.3 | Nov 12, 2024 | Agregado Flujo 4: List Users External. Endpoint: `/auth/users-external`. Usa `Pagination` del core. **Doble validación de seguridad**: `platform.location_id IS NULL` + LEFT JOIN con `user_location_rol` para garantizar separación absoluta de usuarios internos/externos. **Paginación dual adaptativa**. Sistema de filtros flexible (16 campos filtrables). | Equipo de Desarrollo Goluti |
| 1.4 | Nov 12, 2024 | Agregado Flujo 5: Create Company. Endpoint: `/auth/create-company`. Flujo completo de onboarding de compañía con **clonación inteligente de menús** desde plantilla (`company_id = NULL`). Algoritmo de mapeo para preservar jerarquías padre-hijo. Clonación de permisos. Creación de ubicación principal y usuario admin. **Transaccionalidad completa** con rollback automático. Reutiliza `CreateUserInternalUseCase`. Requiere changelogs v28 y v29. | Equipo de Desarrollo Goluti |

---

**Fin del Documento**


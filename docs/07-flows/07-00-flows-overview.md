# Flujos de Desarrollo - Overview

**Versión**: 1.1  
**Fecha**: Noviembre 2024  
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

### Ejemplo Sugerido 3: Onboarding de Clientes

**Archivo**: `07-03-onboarding-flow.md`

**Contenido**:
- Registro inicial del cliente
- Validación de identidad (KYC)
- Verificación de documentos
- Aprobación manual
- Activación de cuenta
- Notificaciones

### Ejemplo Sugerido 4: Flujo de Pagos

**Archivo**: `07-04-payment-flow.md`

**Contenido**:
- Integración con pasarela de pagos
- Creación de orden de pago
- Procesamiento del pago
- Webhooks de confirmación
- Conciliación bancaria
- Generación de comprobantes

### Ejemplo Sugerido 5: Sistema de Notificaciones

**Archivo**: `07-05-notification-system-flow.md`

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

## Referencias

- **[00-00] Documentation Methodology**: Metodología de documentación
- **[02-00] Entity Flow Overview**: Patrón CRUD estándar
- **[03-00] Business Flow Overview**: Lógica de negocio compleja
- **[01-00] Architecture Overview**: Arquitectura general del sistema

---

## Historial de Cambios

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0 | Nov 2024 | Creación inicial de carpeta Flows. Documentación de Flujo 1: Create User Internal | Equipo de Desarrollo Goluti |
| 1.1 | Nov 2024 | Agregado Flujo 2: Create User External. Endpoint público para crear usuarios externos sin roles corporativos. Platform sin ubicación (location_id = null) | Equipo de Desarrollo Goluti |

---

**Fin del Documento**


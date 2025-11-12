# Documentación Goluti Backend Platform

**Bienvenido a la documentación oficial del Backend Platform de Goluti**

Esta documentación describe la arquitectura, flujos, componentes y especificaciones técnicas del sistema. El proyecto está construido con **FastAPI** siguiendo principios de **Clean Architecture** y **Domain-Driven Design**.

---

## 📚 Índice de Documentación

### 🎯 00. Metodología

Guía sobre cómo está organizada y estructurada esta documentación.

- **[00-00-documentation-methodology.md](./00-methodology/00-00-documentation-methodology.md)** - Metodología de documentación del proyecto

### 🏗️ 01. Arquitectura

Visión general de la arquitectura del sistema, principios y estructura.

- **[01-00-architecture-overview.md](./01-architecture/01-00-architecture-overview.md)** - Visión general de la arquitectura
- **[01-02-project-structure.md](./01-architecture/01-02-project-structure.md)** - Estructura detallada del proyecto

### 📦 02. Entity Flow (Flujo de Entidades)

Documentación del flujo CRUD estándar para entidades del dominio.

- **[02-00-entity-flow-overview.md](./02-entity-flow/02-00-entity-flow-overview.md)** - Visión general del Entity Flow

**Componentes del Entity Flow:**
- Domain Models (Save, Update, Read, Delete, List)
- Use Cases (Lógica de negocio)
- Repository Interfaces (Contratos)
- Repository Implementations (Persistencia)
- Controllers (Orquestación HTTP)
- Routers (Endpoints FastAPI)

**Entidades Disponibles:**
- User, Company, Platform, Location, Language, Currency, Country
- Menu, Permission, Rol, ApiToken, Translation
- CurrencyLocation, MenuPermission, RolPermission, UserLocationRol

### 💼 03. Business Flow (Flujo de Lógica de Negocio)

Documentación de procesos de negocio complejos que involucran múltiples entidades.

- **[03-00-business-flow-overview.md](./03-business-flow/03-00-business-flow-overview.md)** - Visión general del Business Flow
- **[03-05-auth-flow-specification.md](./03-business-flow/03-05-auth-flow-specification.md)** - Especificación completa del flujo de autenticación

**Módulos de Negocio:**
- **Auth**: Login, Logout, Refresh Token, Create API Token, Create Company

**📁 Organización de Casos de Uso:**
- Cada flujo de negocio tiene su propia carpeta dentro de `auth/`
- Todos los casos de uso relacionados (principal + auxiliares) van en la misma carpeta
- Ver sección 7.6 del Business Flow Overview para detalles completos

### 🔧 04. Core Components (Componentes Transversales)

Documentación de componentes utilizados por todas las capas del sistema.

- **[04-00-core-overview.md](./04-core-components/04-00-core-overview.md)** - Visión general de componentes core

**Componentes Core:**
- **Configuration**: Gestión de variables de entorno y settings
- **Middleware**: CORS, Rate Limiting, Redirects
- **Wrappers**: Decoradores para permisos, transacciones, roles
- **Enums**: Tipos enumerados (permisos, mensajes, notificaciones)
- **Models**: Modelos compartidos (Config, Response, Filter, Pagination)
- **Classes**: Utilidades (Token, Password, Message)
- **Methods**: Funciones utilitarias (get_config, get_filter)

### 🗄️ 05. Infrastructure (Infraestructura)

Documentación de la capa de infraestructura (base de datos, web).

- **[05-02-database-entities.md](./05-infrastructure/05-02-database-entities.md)** - Entidades de base de datos

**Documentación de Database Entities:**
- Convención de nomenclatura: Entity → Tabla
- Los nombres de entities corresponden exactamente a nombres de tablas
- Ejemplo: `User` (código) → `user` (tabla PostgreSQL)
- Listado completo de 16 entities del sistema
- Estructura de una entity SQLAlchemy
- Foreign keys y relaciones

**Pendiente:**
- Configuración de base de datos
- Mappers
- Repository implementations

### 🌐 06. API Reference (Referencia de API)

Documentación de endpoints HTTP, formatos de request/response.

- **[06-03-list-services-specification.md](./06-api-reference/06-03-list-services-specification.md)** - Especificación de servicios List y sistema de filtros

**Especificaciones de API:**
- Sistema de filtros avanzado (AND, OR, operadores)
- Paginación y límites
- Formatos de request y response
- Códigos de estado HTTP
- Manejo de errores

### 🔄 07. Flows (Flujos de Desarrollo)

Documentación de desarrollos nuevos, flujos específicos e integraciones.

- **[07-00-flows-overview.md](./07-flows/07-00-flows-overview.md)** - Visión general de flujos de desarrollo

**Tipos de Flujos:**
- **Flujos de Proceso de Negocio**: Onboarding, aprobaciones, pagos
- **Flujos de Integración**: APIs externas, webhooks, sistemas legacy
- **Features Complejas**: Notificaciones, reportes, auditoría
- **Flujos de Migración**: Migración de datos, transformaciones

**Flujos Implementados:**
- **[Create User Internal](./07-flows/07-01-create-user-internal-flow.md)**: Creación de usuarios internos con múltiples roles por ubicación (requiere rol ADMIN)
- **[Create User External](./07-flows/07-02-create-user-external-flow.md)**: Registro público de usuarios externos sin roles corporativos (endpoint público)
- **[List Users by Location](./07-flows/07-03-list-users-by-location-flow.md)**: Consulta paginada de usuarios internos por ubicación (`/auth/users-internal`) con JOINs y filtros avanzados
- **[List Users External](./07-flows/07-04-list-users-external-flow.md)**: Consulta paginada de usuarios externos/clientes (`/auth/users-external`). INNER JOIN entre `user` y `platform`, LEFT JOIN con `user_location_rol` para doble validación de seguridad: 1) `platform.location_id IS NULL`, 2) `user_location_rol.id IS NULL`. Retorna 16 campos (user + platform, sin password). Filtros flexibles y paginación dual

**Ejemplos Sugeridos:**
- Onboarding de clientes
- Integración con pasarela de pagos
- Sistema de notificaciones multi-canal
- Aprobación de documentos

### 📋 08. Patterns and Practices (Patrones y Prácticas)

Mejores prácticas, estándares de código y patrones de diseño.

**Pendiente de documentación detallada**

### 🚀 09. Deployment (Despliegue)

Configuración de despliegue, Docker, CI/CD.

**Pendiente de documentación detallada**

---

## 🚀 Inicio Rápido

### Para Nuevos Desarrolladores

Si eres nuevo en el proyecto, te recomendamos leer los documentos en este orden:

1. **[Metodología de Documentación](./00-methodology/00-00-documentation-methodology.md)** - Entiende cómo está organizada la documentación
2. **[Architecture Overview](./01-architecture/01-00-architecture-overview.md)** - Conoce la arquitectura general del sistema
3. **[Project Structure](./01-architecture/01-02-project-structure.md)** - Familiarízate con la estructura de carpetas
4. **[Entity Flow Overview](./02-entity-flow/02-00-entity-flow-overview.md)** - Aprende el flujo CRUD estándar
5. **[Business Flow Overview](./03-business-flow/03-00-business-flow-overview.md)** - Entiende la lógica de negocio compleja
6. **[Core Components](./04-core-components/04-00-core-overview.md)** - Conoce los componentes transversales

### Para Implementar una Nueva Entidad

1. Lee **[Entity Flow Overview](./02-entity-flow/02-00-entity-flow-overview.md)**
2. Sigue la estructura existente de cualquier entidad (ej: User)
3. Crea los componentes necesarios:
   - Domain Models
   - Use Cases
   - Repository Interface
   - Repository Implementation
   - Database Entity
   - Mappers
   - Controller
   - Router

### Para Implementar Lógica de Negocio

1. Lee **[Business Flow Overview](./03-business-flow/03-00-business-flow-overview.md)**
2. Revisa **[Auth Flow Specification](./03-business-flow/03-05-auth-flow-specification.md)** como ejemplo
3. Crea los componentes necesarios:
   - Business Models (Request/Response)
   - Business Use Cases (orquestador + sub-use cases)
   - Business Controller
   - Business Router

---

## 🎯 Arquitectura en Resumen

### Principios

- **Clean Architecture**: Separación clara de capas
- **Domain-Driven Design**: Modelo de dominio rico
- **SOLID**: Principios de diseño orientado a objetos
- **Separation of Concerns**: Cada componente tiene una responsabilidad única

### Capas

```
┌─────────────────────────────────────┐
│     Presentation (Web/HTTP)         │
│  - Routers (FastAPI)                │
│  - Controllers                      │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│          Domain Layer               │
│  - Use Cases (Business Logic)       │
│  - Domain Models                    │
│  - Repository Interfaces            │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│     Infrastructure Layer            │
│  - Repository Implementations       │
│  - Database Entities (SQLAlchemy)   │
│  - Mappers                          │
└─────────────────────────────────────┘
```

### Dos Flujos Principales

#### 1. **Entity Flow** (CRUD)
- Operaciones estándar: Save, Update, List, Read, Delete
- Patrón repetible para todas las entidades
- Ejemplo: User, Company, Platform

#### 2. **Business Flow** (Lógica Compleja)
- Operaciones personalizadas que involucran múltiples entidades
- Orquestación de use cases
- Ejemplo: Auth (Login, Logout, Refresh Token)

---

## 🔑 Conceptos Clave

### Config
Objeto que contiene:
- Sesión de base de datos asíncrona
- Token de acceso decodificado
- Idioma del request
- Tipo de respuesta (object/dict)

### Response Wrapper
Todas las respuestas HTTP siguen el mismo formato:
```json
{
  "message_type": "temporary | static",
  "notification_type": "success | error | warning | info",
  "message": "Mensaje localizado",
  "response": { /* datos */ } | null
}
```

### Decoradores (Wrappers)
- `@check_permissions([...])`: Verifica permisos del usuario
- `@execute_transaction`: Tracking de transacciones
- `@execute_transaction_route`: Tracking en nivel de router

### Sistema de Filtros
Sistema avanzado de filtros con:
- Operadores: `==`, `>`, `<`, `>=`, `<=`, `!=`, `like`, `in`
- AND lógico (por defecto)
- OR lógico (usando grupos)
- Paginación (skip/limit)

---

## 🛠️ Tecnologías

- **FastAPI**: Framework web asíncrono
- **Pydantic**: Validación y serialización de datos
- **SQLAlchemy**: ORM asíncrono
- **PostgreSQL**: Base de datos relacional
- **JWT**: Autenticación stateless
- **Bcrypt**: Hash de contraseñas
- **Uvicorn**: Servidor ASGI
- **Docker**: Contenedorización
- **AWS**: Despliegue en la nube

---

## 📖 Convenciones

### Nomenclatura de Archivos
- **snake_case**: Archivos y módulos Python
- **PascalCase**: Clases
- **SCREAMING_SNAKE_CASE**: Constantes

### Estructura de Archivos
```
{entity}/
├── {entity}.py              # Modelo principal
├── {entity}_save.py         # Modelo para crear
├── {entity}_update.py       # Modelo para actualizar
├── {entity}_read.py         # Modelo para leer
├── {entity}_delete.py       # Modelo para eliminar
└── index.py                 # Exportaciones
```

### Patrones de Nombres
- Use Cases: `{Entity}{Operation}UseCase`
- Repositories: `{Entity}Repository`, `I{Entity}Repository`
- Controllers: `{Entity}Controller`
- Routers: `{entity}_router.py`

---

## 📝 Contribuir a la Documentación

### Cuándo Actualizar

- Al agregar nuevas entidades
- Al modificar flujos existentes
- Al cambiar APIs públicas
- Al tomar decisiones arquitectónicas importantes

### Cómo Actualizar

1. Identifica los documentos afectados
2. Sigue la metodología definida en **[00-00-documentation-methodology.md](./00-methodology/00-00-documentation-methodology.md)**
3. Actualiza contenido, versión y fecha
4. Agrega entrada en "Historial de Cambios"
5. Actualiza referencias cruzadas si es necesario

---

## 🆘 Soporte

Para preguntas o clarificaciones sobre la documentación o el código:

1. Revisa la documentación relevante
2. Busca ejemplos en el código existente
3. Consulta con el equipo de desarrollo
4. Actualiza la documentación si encuentras información faltante

---

## 📜 Licencia

Este proyecto y su documentación son propiedad de **Goluti**.

---

## 🏆 Estado de Documentación

| Sección | Estado | Completitud |
|---------|--------|-------------|
| 00. Metodología | ✅ Completo | 100% |
| 01. Arquitectura | 🟡 Parcial | 40% |
| 02. Entity Flow | ✅ Completo | 90% |
| 03. Business Flow | ✅ Completo | 80% |
| 04. Core Components | ✅ Completo | 100% |
| 05. Infrastructure | 🟡 Parcial | 20% |
| 06. API Reference | 🟡 Parcial | 30% |
| 07. Flows | ✅ Completo | 100% |
| 08. Patterns | ❌ Pendiente | 0% |
| 09. Deployment | ❌ Pendiente | 0% |

**Leyenda:**
- ✅ Completo: Documentación suficiente para uso
- 🟡 Parcial: Documentación básica disponible
- ❌ Pendiente: Sin documentación

---

## 📅 Última Actualización

**Fecha**: Noviembre 11, 2024  
**Versión de Documentación**: 1.4  
**Versión del Proyecto**: 1.0.0

---

**Equipo de Desarrollo Goluti**


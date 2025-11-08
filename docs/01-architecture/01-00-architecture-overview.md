# Visión General de la Arquitectura - Goluti Backend Platform

**Versión**: 1.0  
**Fecha**: Noviembre 2024  
**Estado**: Vigente  
**Autor(es)**: Equipo de Desarrollo Goluti

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Principios Arquitectónicos](#principios-arquitectónicos)
3. [Arquitectura de Alto Nivel](#arquitectura-de-alto-nivel)
4. [Capas del Sistema](#capas-del-sistema)
5. [Flujos Principales](#flujos-principales)
6. [Tecnologías Utilizadas](#tecnologías-utilizadas)
7. [Decisiones Arquitectónicas](#decisiones-arquitectónicas)
8. [Referencias](#referencias)

---

## Introducción

**Goluti Backend Platform** es una aplicación backend desarrollada con **FastAPI** que implementa una arquitectura limpia (Clean Architecture) y principios de diseño dirigido por el dominio (Domain-Driven Design). El sistema proporciona servicios RESTful para la gestión de entidades de negocio y operaciones complejas de lógica de negocio.

### Objetivo del Sistema

- Proporcionar una API REST robusta y escalable
- Implementar operaciones CRUD sobre entidades de dominio
- Ejecutar lógica de negocio compleja (autenticación, autorización, etc.)
- Mantener separación clara de responsabilidades
- Facilitar testing, mantenimiento y evolución del código

---

## Principios Arquitectónicos

### 1. Clean Architecture (Arquitectura Limpia)

El sistema sigue los principios de Clean Architecture propuestos por Robert C. Martin:

- **Independencia de frameworks**: La lógica de negocio no depende de FastAPI
- **Testeable**: Lógica de negocio probable sin UI, DB o servicios externos
- **Independencia de UI**: La UI (API REST) puede cambiar sin afectar el negocio
- **Independencia de BD**: Puede cambiar de PostgreSQL a otro motor sin afectar el dominio
- **Independencia de agentes externos**: Lógica de negocio no conoce detalles externos

### 2. Domain-Driven Design (DDD)

- **Ubiquitous Language**: Lenguaje compartido entre negocio y código
- **Bounded Contexts**: Contextos claramente delimitados (Entity, Business)
- **Domain Models**: Modelos de dominio ricos y expresivos
- **Repository Pattern**: Abstracción del acceso a datos
- **Use Cases**: Casos de uso que representan intenciones del usuario

### 3. SOLID Principles

- **S**ingle Responsibility: Cada clase tiene una única razón para cambiar
- **O**pen/Closed: Abierto para extensión, cerrado para modificación
- **L**iskov Substitution: Interfaces coherentes y sustituibles
- **I**nterface Segregation: Interfaces específicas, no generales
- **D**ependency Inversion: Depender de abstracciones, no de implementaciones

### 4. Separation of Concerns

Separación clara entre:
- **Presentación** (Web/API)
- **Lógica de Negocio** (Use Cases)
- **Acceso a Datos** (Repositories)
- **Infraestructura** (Database, External Services)

---

## Arquitectura de Alto Nivel

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENTE                              │
│                    (Frontend, Apps, APIs)                    │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/HTTPS
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  FastAPI Application (main.py)                       │   │
│  │  - Middleware (CORS, Rate Limit, Redirects)          │   │
│  │  - Routers (Entity, Business, WebSocket)             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Web Layer                                            │   │
│  │  - Controllers (Entity, Business)                     │   │
│  │  - Route Configuration                                │   │
│  │  - Request/Response Mapping                           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                     DOMAIN LAYER                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Use Cases (Application Logic)                        │   │
│  │  - Entity Use Cases (CRUD)                            │   │
│  │  - Business Use Cases (Auth, Complex Logic)           │   │
│  │                                                        │   │
│  │  Domain Models                                         │   │
│  │  - Entity Models (Save, Read, Update, Delete, List)   │   │
│  │  - Business Models (Request/Response)                 │   │
│  │                                                        │   │
│  │  Repository Interfaces                                 │   │
│  │  - IUserRepository, IPlatformRepository, etc.         │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Database Layer                                        │   │
│  │  - Repository Implementations                          │   │
│  │  - Database Entities (SQLAlchemy)                      │   │
│  │  - Mappers (Entity ↔ Domain)                          │   │
│  │  - Database Configuration                              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE (PostgreSQL)                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Capas del Sistema

### 1. **Core Layer** (`src/core/`)

Componentes transversales utilizados por todas las capas:

- **Config**: Configuración del sistema y entorno
- **Middleware**: CORS, Rate Limiting, Redirects
- **Wrappers**: Decoradores para transacciones, permisos, roles
- **Enums**: Tipos enumerados (Permisos, Tipos de Mensajes, etc.)
- **Models**: Modelos compartidos (Config, Response, Filter, etc.)
- **Classes**: Clases auxiliares (Token, Password, Message)

### 2. **Domain Layer** (`src/domain/`)

Núcleo del negocio, independiente de frameworks:

- **Models**: 
  - `entities/`: Modelos de dominio para entidades CRUD
  - `business/`: Modelos de dominio para lógica de negocio
  
- **Services**:
  - `use_cases/`: Casos de uso (lógica de aplicación)
  - `repositories/`: Interfaces de repositorios (contratos)

### 3. **Infrastructure Layer** (`src/infrastructure/`)

Implementaciones concretas de infraestructura:

- **Web**:
  - `routes/`: Configuración de rutas FastAPI
  - `controller/`: Controladores HTTP
  - `entities_routes/`: Routers para entidades
  - `business_routes/`: Routers para lógica de negocio
  - `websockets_routes/`: Routers para WebSockets

- **Database**:
  - `config/`: Configuración de conexión a BD
  - `entities/`: Entidades SQLAlchemy
  - `repositories/`: Implementaciones de repositorios
  - `mappers/`: Mapeo entre Entity DB y Domain Model

---

## Flujos Principales

### Flujo 1: Entity Flow (CRUD)

Operaciones estándar sobre entidades del dominio:

```
┌─────────┐     ┌────────────┐     ┌──────────┐     ┌────────────┐     ┌──────────┐
│ Cliente │────▶│   Router   │────▶│Controller│────▶│  UseCase   │────▶│Repository│
│  HTTP   │     │  (FastAPI) │     │   (Web)  │     │  (Domain)  │     │   (DB)   │
└─────────┘     └────────────┘     └──────────┘     └────────────┘     └──────────┘
                      │                  │                  │                  │
                      │                  │                  │                  ▼
                      │                  │                  │            ┌──────────┐
                      │                  │                  │            │ Database │
                      │                  │                  │◀───────────│PostgreSQL│
                      │                  │                  │            └──────────┘
                      │                  │◀─────────────────│
                      │◀─────────────────│
                      ▼
                 ┌─────────┐
                 │Response │
                 │  JSON   │
                 └─────────┘
```

**Operaciones soportadas:**
- **Save** (`POST /{entity}`): Crear nueva entidad
- **Update** (`PUT /{entity}`): Actualizar entidad existente
- **List** (`POST /{entity}/list`): Listar entidades con filtros
- **Read** (`GET /{entity}/{id}`): Leer una entidad por ID
- **Delete** (`DELETE /{entity}/{id}`): Eliminar una entidad

### Flujo 2: Business Flow

Lógica de negocio compleja que puede involucrar múltiples entidades:

```
┌─────────┐     ┌────────────┐     ┌────────────┐     ┌──────────────┐
│ Cliente │────▶│   Router   │────▶│ Controller │────▶│  Business    │
│  HTTP   │     │  (FastAPI) │     │ (Business) │     │  Use Case    │
└─────────┘     └────────────┘     └────────────┘     └──────┬───────┘
                      │                  │                    │
                      │                  │                    ├──▶ UseCase 1
                      │                  │                    ├──▶ UseCase 2
                      │                  │                    ├──▶ UseCase 3
                      │                  │                    └──▶ UseCase N
                      │                  │◀───────────────────┘
                      │◀─────────────────│
                      ▼
                 ┌─────────┐
                 │Response │
                 │  JSON   │
                 └─────────┘
```

**Ejemplos:**
- **Auth Login**: Valida usuario, genera tokens, carga configuración
- **Refresh Token**: Renueva token de acceso
- **Create API Token**: Genera tokens de API
- **Logout**: Invalida refresh token

---

## Tecnologías Utilizadas

### Backend Framework
- **FastAPI**: Framework web moderno, rápido y con validación automática
- **Pydantic**: Validación de datos y serialización
- **Uvicorn**: Servidor ASGI de alto rendimiento

### Base de Datos
- **PostgreSQL**: Base de datos relacional principal
- **SQLAlchemy**: ORM asíncrono para Python
- **Alembic**: Herramienta de migraciones (implícita)

### Seguridad
- **JWT (JSON Web Tokens)**: Autenticación stateless
- **Bcrypt**: Hash de contraseñas
- **Bearer Authentication**: Esquema de autenticación

### Utilidades
- **Python 3.11+**: Lenguaje de programación
- **python-dotenv**: Gestión de variables de entorno
- **AsyncIO**: Programación asíncrona

---

## Decisiones Arquitectónicas

### 1. Arquitectura Asíncrona

**Decisión**: Usar programación asíncrona con `async/await`  
**Razón**: Mayor rendimiento y escalabilidad para operaciones I/O (base de datos, APIs externas)  
**Impacto**: Todos los use cases y repositories son asíncronos

### 2. Clean Architecture

**Decisión**: Separación estricta en capas (Domain, Infrastructure, Core)  
**Razón**: Mantenibilidad, testabilidad e independencia de frameworks  
**Impacto**: Más archivos y estructura, pero mayor flexibilidad a largo plazo

### 3. Repository Pattern

**Decisión**: Usar interfaces de repositorio en el dominio  
**Razón**: Desacoplar lógica de negocio del acceso a datos  
**Impacto**: Facilita testing con mocks y cambio de implementación de BD

### 4. Wrappers con Decoradores

**Decisión**: Usar decoradores para transacciones, permisos y tracking  
**Razón**: Cross-cutting concerns sin contaminar lógica de negocio  
**Impacto**: Código más limpio y mantenible

### 5. Dos Tipos de Flujos (Entity y Business)

**Decisión**: Separar CRUD estándar de lógica de negocio compleja  
**Razón**: Claridad en la estructura y diferentes necesidades de modelado  
**Impacto**: Escalabilidad y facilidad para agregar nuevas entidades

### 6. Response Wrapper Unificado

**Decisión**: Todas las respuestas siguen el mismo formato  
**Razón**: Consistencia en la API y manejo uniforme de errores  
**Impacto**: Clientes pueden procesar respuestas de forma predecible

### 7. Sistema de Filtros Avanzado

**Decisión**: Sistema de filtros flexible con operadores y grupos  
**Razón**: Permitir consultas complejas sin crear endpoints específicos  
**Impacto**: Mayor flexibilidad para clientes, complejidad en implementación

---

## Referencias

- **[01-01] Clean Architecture Principles**: Detalles de principios aplicados
- **[01-02] Project Structure**: Estructura detallada del proyecto
- **[01-03] Layers and Responsibilities**: Responsabilidades de cada capa
- **[01-04] Dependency Flow**: Flujo de dependencias entre capas
- **[02-00] Entity Flow Overview**: Documentación del flujo de entidades
- **[03-00] Business Flow Overview**: Documentación del flujo de negocio

---

## Historial de Cambios

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0 | Nov 2024 | Creación inicial de visión arquitectónica | Equipo de Desarrollo Goluti |

---

**Fin del Documento**


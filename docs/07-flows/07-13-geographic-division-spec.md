# 07-13: Divisiones Geográficas (Geographic Division)

## Información del Documento

| Campo | Detalle |
|-------|---------|
| **Versión** | 3.6 |
| **Última Actualización** | Enero 2026 |
| **Autor** | Equipo de Desarrollo Goluti |
| **Estado** | Borrador |

---

## Resumen Ejecutivo

Este documento especifica la creación de un sistema de **divisiones geográficas jerárquicas** que permita definir la estructura territorial de forma flexible y recursiva. El objetivo es que al registrar un `location` se pueda determinar su ubicación geográfica con la mayor precisión posible.

**Cambio arquitectónico clave:** La tabla `country` desaparece como entidad independiente. Los países pasan a ser **nodos raíz** (level 0, `top_id = NULL`) dentro de `geo_division`. Toda referencia que antes apuntaba a `country(id)` ahora apunta a `geo_division(id)` donde el nodo tiene tipo COUNTRY.

**Características principales:**
- Tabla `geo_division_type` para definir tipos de división (COUNTRY, DEPARTMENT, CITY, etc.) de forma dinámica
- Tabla recursiva `geo_division` con `id` y `top_id` para soportar jerarquías de profundidad variable
- Los países son nodos raíz de la jerarquía (level 0, type COUNTRY)
- Flexible por país: Colombia puede tener Departamentos > Ciudades > Comunas, mientras que otro país puede tener Estados > Condados > Ciudades
- Migración de la tabla `country` hacia `geo_division`
- Tabla `location` actualizada: `country_id` y `city_id` apuntando a nodos de `geo_division`, **campo `city` VARCHAR eliminado** (no está en producción)
- Ambas tablas nuevas (`geo_division_type` y `geo_division`) con flujo completo de entity (CRUD)
- Endpoints de negocio dinámicos: listar países, listar divisiones por tipo y país, etc.
- Configuración inicial para Colombia con 3 niveles: Departamentos > Ciudades > Comunas/Localidades

---

## Tabla de Contenidos

1. [Problema a Resolver](#problema-a-resolver)
2. [Diseño de Base de Datos](#diseño-de-base-de-datos)
3. [Impacto en Tablas Existentes](#impacto-en-tablas-existentes)
4. [Datos Iniciales - Colombia](#datos-iniciales---colombia)
5. [Flujos de Entity (CRUD)](#flujos-de-entity-crud)
6. [Flujos de Negocio (Endpoints Dinámicos)](#flujos-de-negocio-endpoints-dinámicos)
7. [Fases de Implementación](#fases-de-implementación)
8. [Diagrama ER](#diagrama-er)
9. [Consideraciones](#consideraciones)

---

## Problema a Resolver

### Situación Actual

La tabla `location` almacena la ubicación de una sede con un campo `city VARCHAR(100)` que es texto libre y un `country_id` que apunta a una tabla `country` separada sin jerarquía interna:

```
country actual:                    location actual:
├── id                             ├── id
├── name                           ├── company_id
├── code (CO, MX, etc.)           ├── country_id     → country(id)
├── phone_code (+57, etc.)        ├── name
└── state                          ├── address
                                   ├── city           ← VARCHAR(100) texto libre
                                   ├── phone
                                   ├── email
                                   ├── main_location
                                   └── state
```

**Problemas identificados:**
1. **Sin normalización**: "Bogotá", "bogota", "BOGOTA D.C." son valores distintos
2. **Sin jerarquía**: No se puede saber a qué departamento pertenece una ciudad
3. **Sin flexibilidad**: Cada país tiene una estructura territorial diferente
4. **Sin validación**: No hay forma de validar que una ciudad exista dentro de un país
5. **Tabla `country` aislada**: No hay relación jerárquica entre país, departamento y ciudad

### Solución Propuesta

Crear un sistema jerárquico unificado donde **el país es el nodo raíz** y toda la estructura territorial se deriva de él:

```
geo_division: Colombia (type: COUNTRY, level: 0, top_id: NULL)
├── geo_division: Antioquia (type: DEPARTMENT, level: 1)
│   ├── geo_division: Medellín (type: CITY, level: 2)
│   │   ├── geo_division: El Poblado (type: COMMUNE, level: 3)
│   │   ├── geo_division: Laureles (type: COMMUNE, level: 3)
│   │   └── geo_division: Belén (type: COMMUNE, level: 3)
│   ├── geo_division: Envigado (type: CITY, level: 2)
│   └── geo_division: Bello (type: CITY, level: 2)
├── geo_division: Bogotá D.C. (type: DEPARTMENT, level: 1)
│   └── geo_division: Bogotá (type: CITY, level: 2)
│       ├── geo_division: Usaquén (type: LOCALITY, level: 3)
│       ├── geo_division: Chapinero (type: LOCALITY, level: 3)
│       └── geo_division: Suba (type: LOCALITY, level: 3)
└── geo_division: Valle del Cauca (type: DEPARTMENT, level: 1)
    ├── geo_division: Cali (type: CITY, level: 2)
    │   ├── geo_division: Comuna 2 (type: COMMUNE, level: 3)
    │   └── geo_division: Comuna 17 (type: COMMUNE, level: 3)
    └── geo_division: Palmira (type: CITY, level: 2)
```

---

## Diseño de Base de Datos

### Nueva Tabla: `geo_division_type`

Define los tipos de división geográfica de forma dinámica. Reemplaza el uso de enums hardcodeados.

```sql
CREATE TABLE geo_division_type (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL UNIQUE,     -- COUNTRY, DEPARTMENT, CITY, etc.
    label VARCHAR(255) NOT NULL,          -- Etiqueta para mostrar: "País", "Departamento", "Ciudad"
    description TEXT,                     -- Descripción del tipo
    state BOOLEAN NOT NULL DEFAULT TRUE,
    created_date TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_date TIMESTAMP NOT NULL DEFAULT NOW()
);
```

#### Descripción de Columnas

| Columna | Tipo | Nulable | Descripción |
|---------|------|---------|-------------|
| `id` | UUID | NO | Identificador único |
| `name` | VARCHAR(50) | NO | Código del tipo, único (COUNTRY, DEPARTMENT, CITY, etc.) |
| `label` | VARCHAR(255) | NO | Etiqueta para UI ("País", "Departamento", "Ciudad") |
| `description` | TEXT | SÍ | Descripción opcional |
| `state` | BOOLEAN | NO | Estado activo/inactivo |
| `created_date` | TIMESTAMP | NO | Fecha de creación |
| `updated_date` | TIMESTAMP | NO | Fecha de última actualización |

#### Registros Iniciales

| name | label | Descripción |
|------|-------|-------------|
| COUNTRY | País | Nodo raíz, equivale a la antigua tabla country |
| DEPARTMENT | Departamento | División de primer nivel (Colombia) |
| STATE | Estado | División de primer nivel (México, USA) |
| PROVINCE | Provincia | División de primer nivel (Argentina, España) |
| REGION | Región | División intermedia |
| CITY | Ciudad | Ciudad principal |
| MUNICIPALITY | Municipio | Municipio |
| COMMUNE | Comuna | Comuna (Medellín, Cali, etc.) |
| LOCALITY | Localidad | Localidad (Bogotá) |
| NEIGHBORHOOD | Barrio | Barrio o sector |
| DISTRICT | Distrito | Distrito |
| ZONE | Zona | Zona geográfica |

---

### Nueva Tabla: `geo_division`

Tabla recursiva que contiene toda la jerarquía geográfica, incluyendo los países como nodos raíz.

```sql
CREATE TABLE geo_division (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    top_id UUID,                                    -- NULL = nodo raíz (países)
    geo_division_type_id UUID NOT NULL,             -- FK a geo_division_type
    name VARCHAR(255) NOT NULL,
    code VARCHAR(20),                               -- Código oficial (ISO 3166, DANE, etc.)
    phone_code VARCHAR(10),                         -- Solo para nodos tipo COUNTRY
    level INTEGER NOT NULL DEFAULT 0,               -- 0=country, 1=department, 2=city, 3=commune...
    state BOOLEAN NOT NULL DEFAULT TRUE,
    created_date TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_date TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT fk_geo_division_top 
        FOREIGN KEY (top_id) REFERENCES geo_division(id) ON DELETE RESTRICT,
    CONSTRAINT fk_geo_division_type 
        FOREIGN KEY (geo_division_type_id) REFERENCES geo_division_type(id) ON DELETE RESTRICT
);
```

#### Descripción de Columnas

| Columna | Tipo | Nulable | Descripción |
|---------|------|---------|-------------|
| `id` | UUID | NO | Identificador único |
| `top_id` | UUID FK | SÍ | Nodo padre. `NULL` = nodo raíz (países) |
| `geo_division_type_id` | UUID FK | NO | Tipo de división (FK a `geo_division_type`) |
| `name` | VARCHAR(255) | NO | Nombre de la división geográfica |
| `code` | VARCHAR(20) | SÍ | Código oficial (ISO 3166 para países, DANE para Colombia, etc.) |
| `phone_code` | VARCHAR(10) | SÍ | Código telefónico del país. Solo aplica para nodos tipo COUNTRY |
| `level` | INTEGER | NO | Nivel jerárquico (0=country, 1=department, 2=city, 3=commune, etc.) |
| `state` | BOOLEAN | NO | Estado activo/inactivo |
| `created_date` | TIMESTAMP | NO | Fecha de creación |
| `updated_date` | TIMESTAMP | NO | Fecha de última actualización |

#### Índices

```sql
CREATE INDEX idx_geo_division_top_id ON geo_division(top_id);
CREATE INDEX idx_geo_division_type_id ON geo_division(geo_division_type_id);
CREATE INDEX idx_geo_division_level ON geo_division(level);
CREATE INDEX idx_geo_division_code ON geo_division(code);
CREATE INDEX idx_geo_division_top_type ON geo_division(top_id, geo_division_type_id);
```

---

## Impacto en Tablas Existentes

### Tabla `country` - SE ELIMINA

La tabla `country` **desaparece**. Los países pasan a ser nodos raíz en `geo_division` con:
- `top_id = NULL`
- `level = 0`
- `geo_division_type_id` = ID del tipo COUNTRY
- `code` = código ISO (CO, MX, AR, etc.)
- `phone_code` = código telefónico (+57, +52, +54, etc.)

**Migración de datos:** Los registros existentes en `country` se migran a `geo_division` manteniendo sus IDs originales para no romper FKs existentes.

#### Tablas que referenciaban `country` y su nuevo destino

| Tabla | Columna Actual | Apuntaba a | Nuevo Destino |
|-------|---------------|------------|---------------|
| `location` | `country_id` | `country(id)` | `geo_division(id)` (nodo COUNTRY) |
| `user_country` | `country_id` | `country(id)` | `geo_division(id)` (nodo COUNTRY) |

---

### Tabla `location` - Cambios Requeridos

La tabla `location` se actualiza para referenciar nodos de `geo_division` en lugar de la tabla `country`. **El campo `city VARCHAR(100)` se elimina** ya que no está en producción:

1. **`country_id`**: Cambia FK de `country(id)` a `geo_division(id)` apuntando a un nodo tipo COUNTRY
2. **`city`**: Se **elimina** el campo VARCHAR y se reemplaza por `city_id UUID` apuntando a un nodo tipo CITY en `geo_division`
3. **`latitude`**: Nuevo campo `DECIMAL(10,8)` nullable para coordenada de latitud (-90 a 90)
4. **`longitude`**: Nuevo campo `DECIMAL(11,8)` nullable para coordenada de longitud (-180 a 180)
5. **`google_place_id`**: Nuevo campo `VARCHAR(255)` nullable para integración con Google Maps Places API

```sql
-- 1. Eliminar FK antigua de country
ALTER TABLE location DROP CONSTRAINT IF EXISTS location_country_id_fkey;

-- 2. Redirigir country_id a geo_division
ALTER TABLE location ADD CONSTRAINT fk_location_country 
    FOREIGN KEY (country_id) REFERENCES geo_division(id) ON DELETE RESTRICT;

-- 3. Eliminar campo city (no está en producción)
ALTER TABLE location DROP COLUMN city;

-- 4. Agregar columna city_id
ALTER TABLE location ADD COLUMN city_id UUID;

ALTER TABLE location ADD CONSTRAINT fk_location_city 
    FOREIGN KEY (city_id) REFERENCES geo_division(id) ON DELETE RESTRICT;

CREATE INDEX idx_location_city_id ON location(city_id);

-- 5. Agregar coordenadas geográficas (nullable para futura implementación)
ALTER TABLE location ADD COLUMN latitude DECIMAL(10, 8);
ALTER TABLE location ADD COLUMN longitude DECIMAL(11, 8);

ALTER TABLE location ADD CONSTRAINT chk_location_latitude 
    CHECK (latitude IS NULL OR (latitude >= -90 AND latitude <= 90));

ALTER TABLE location ADD CONSTRAINT chk_location_longitude 
    CHECK (longitude IS NULL OR (longitude >= -180 AND longitude <= 180));

CREATE INDEX idx_location_coordinates ON location(latitude, longitude) 
    WHERE latitude IS NOT NULL AND longitude IS NOT NULL;

-- 6. Agregar Google Place ID (nullable, para integración con Google Maps)
ALTER TABLE location ADD COLUMN google_place_id VARCHAR(255);
```

**Resultado en la tabla `location`:**

```
location (actualizada):
├── id
├── company_id        → company(id)
├── country_id        → geo_division(id)    -- Ahora apunta a geo_division (nodo COUNTRY)
├── city_id           → geo_division(id)    -- NUEVO: reemplaza campo city VARCHAR
├── name
├── address
├── latitude          ← NUEVO (DECIMAL, nullable) coordenada de latitud
├── longitude         ← NUEVO (DECIMAL, nullable) coordenada de longitud
├── google_place_id   ← NUEVO (VARCHAR, nullable) ID de Google Maps Places
├── phone
├── email
├── main_location
└── state
```

> **Nota sobre coordenadas:** Los campos `latitude` y `longitude` son nullable para permitir implementación futura. Usan `DECIMAL(10,8)` y `DECIMAL(11,8)` respectivamente, lo que da una precisión de ~1.1mm (más que suficiente para ubicar una sede). Se incluyen CHECK constraints para validar rangos geográficos válidos y un índice parcial que solo indexa filas con coordenadas no nulas.

> **Nota sobre `google_place_id`:** Es un identificador como `ChIJd8BlQ2BZwokRAFUEcm_qrcA` que Google Maps asigna a cada lugar. Permite: obtener fotos del lugar, reviews, recalcular dirección formateada y obtener lat/lng actualizadas. Es útil si el frontend usa Google Maps Places Autocomplete para la búsqueda de direcciones.

---

### Tabla `user_country` - Cambios Requeridos

La tabla `user_country` actualiza su FK de `country(id)` a `geo_division(id)`:

```sql
-- 1. Eliminar FK antigua
ALTER TABLE user_country DROP CONSTRAINT IF EXISTS fk_user_country_country;

-- 2. Redirigir a geo_division
ALTER TABLE user_country ADD CONSTRAINT fk_user_country_geo_division 
    FOREIGN KEY (country_id) REFERENCES geo_division(id) ON DELETE RESTRICT;
```

> **Nota:** La columna se sigue llamando `country_id` por claridad semántica, pero ahora apunta a `geo_division(id)` donde el nodo es de tipo COUNTRY.

---

## Datos Iniciales - Colombia

### Tipos de División (geo_division_type)

| name | label |
|------|-------|
| COUNTRY | País |
| DEPARTMENT | Departamento |
| CITY | Ciudad |
| MUNICIPALITY | Municipio |
| STATE | Estado |
| PROVINCE | Provincia |
| REGION | Región |
| COMMUNE | Comuna |
| LOCALITY | Localidad |
| NEIGHBORHOOD | Barrio |
| DISTRICT | Distrito |
| ZONE | Zona |

### País (Level 0 - nodo raíz)

| Código ISO | Nombre | Phone Code | Type | Level |
|------------|--------|------------|------|-------|
| CO | Colombia | +57 | COUNTRY | 0 |

> **Nota:** Se migra el registro existente de la tabla `country` preservando su UUID original.

### Departamentos (Level 1)

Los 33 departamentos (32 + Bogotá D.C.), todos con `top_id` apuntando al nodo Colombia:

| Código DANE | Nombre | Type | Level |
|-------------|--------|------|-------|
| 05 | Antioquia | DEPARTMENT | 1 |
| 08 | Atlántico | DEPARTMENT | 1 |
| 11 | Bogotá D.C. | DEPARTMENT | 1 |
| 13 | Bolívar | DEPARTMENT | 1 |
| 15 | Boyacá | DEPARTMENT | 1 |
| 17 | Caldas | DEPARTMENT | 1 |
| 18 | Caquetá | DEPARTMENT | 1 |
| 19 | Cauca | DEPARTMENT | 1 |
| 20 | Cesar | DEPARTMENT | 1 |
| 23 | Córdoba | DEPARTMENT | 1 |
| 25 | Cundinamarca | DEPARTMENT | 1 |
| 27 | Chocó | DEPARTMENT | 1 |
| 41 | Huila | DEPARTMENT | 1 |
| 44 | La Guajira | DEPARTMENT | 1 |
| 47 | Magdalena | DEPARTMENT | 1 |
| 50 | Meta | DEPARTMENT | 1 |
| 52 | Nariño | DEPARTMENT | 1 |
| 54 | Norte de Santander | DEPARTMENT | 1 |
| 63 | Quindío | DEPARTMENT | 1 |
| 66 | Risaralda | DEPARTMENT | 1 |
| 68 | Santander | DEPARTMENT | 1 |
| 70 | Sucre | DEPARTMENT | 1 |
| 73 | Tolima | DEPARTMENT | 1 |
| 76 | Valle del Cauca | DEPARTMENT | 1 |
| 81 | Arauca | DEPARTMENT | 1 |
| 85 | Casanare | DEPARTMENT | 1 |
| 86 | Putumayo | DEPARTMENT | 1 |
| 88 | San Andrés y Providencia | DEPARTMENT | 1 |
| 91 | Amazonas | DEPARTMENT | 1 |
| 94 | Guainía | DEPARTMENT | 1 |
| 95 | Guaviare | DEPARTMENT | 1 |
| 97 | Vaupés | DEPARTMENT | 1 |
| 99 | Vichada | DEPARTMENT | 1 |

### Ciudades Principales (Level 2)

Ciudades/municipios principales por departamento, con `top_id` apuntando a su departamento:

| Departamento | Código DANE | Ciudad | Type | Level |
|-------------|-------------|--------|------|-------|
| Antioquia | 05001 | Medellín | CITY | 2 |
| Antioquia | 05088 | Bello | CITY | 2 |
| Antioquia | 05266 | Envigado | CITY | 2 |
| Antioquia | 05360 | Itagüí | CITY | 2 |
| Antioquia | 05631 | Sabaneta | CITY | 2 |
| Atlántico | 08001 | Barranquilla | CITY | 2 |
| Atlántico | 08758 | Soledad | CITY | 2 |
| Bogotá D.C. | 11001 | Bogotá | CITY | 2 |
| Bolívar | 13001 | Cartagena | CITY | 2 |
| Boyacá | 15001 | Tunja | CITY | 2 |
| Caldas | 17001 | Manizales | CITY | 2 |
| Caquetá | 18001 | Florencia | CITY | 2 |
| Cauca | 19001 | Popayán | CITY | 2 |
| Cesar | 20001 | Valledupar | CITY | 2 |
| Córdoba | 23001 | Montería | CITY | 2 |
| Cundinamarca | 25754 | Soacha | CITY | 2 |
| Cundinamarca | 25175 | Chía | CITY | 2 |
| Cundinamarca | 25899 | Zipaquirá | CITY | 2 |
| Chocó | 27001 | Quibdó | CITY | 2 |
| Huila | 41001 | Neiva | CITY | 2 |
| La Guajira | 44001 | Riohacha | CITY | 2 |
| Magdalena | 47001 | Santa Marta | CITY | 2 |
| Meta | 50001 | Villavicencio | CITY | 2 |
| Nariño | 52001 | Pasto | CITY | 2 |
| Norte de Santander | 54001 | Cúcuta | CITY | 2 |
| Quindío | 63001 | Armenia | CITY | 2 |
| Risaralda | 66001 | Pereira | CITY | 2 |
| Santander | 68001 | Bucaramanga | CITY | 2 |
| Sucre | 70001 | Sincelejo | CITY | 2 |
| Tolima | 73001 | Ibagué | CITY | 2 |
| Valle del Cauca | 76001 | Cali | CITY | 2 |
| Valle del Cauca | 76109 | Buenaventura | CITY | 2 |
| Valle del Cauca | 76520 | Palmira | CITY | 2 |
| Arauca | 81001 | Arauca | CITY | 2 |
| Casanare | 85001 | Yopal | CITY | 2 |
| Putumayo | 86001 | Mocoa | CITY | 2 |
| San Andrés y Providencia | 88001 | San Andrés | CITY | 2 |
| Amazonas | 91001 | Leticia | CITY | 2 |
| Guainía | 94001 | Inírida | CITY | 2 |
| Guaviare | 95001 | San José del Guaviare | CITY | 2 |
| Vaupés | 97001 | Mitú | CITY | 2 |
| Vichada | 99001 | Puerto Carreño | CITY | 2 |

### Comunas y Localidades (Level 3)

Subdivisiones de las ciudades principales. Bogotá usa **localidades**, las demás ciudades usan **comunas**.

#### Bogotá - Localidades

| Ciudad | Nombre | Type | Level |
|--------|--------|------|-------|
| Bogotá | Usaquén | LOCALITY | 3 |
| Bogotá | Chapinero | LOCALITY | 3 |
| Bogotá | Santa Fe | LOCALITY | 3 |
| Bogotá | San Cristóbal | LOCALITY | 3 |
| Bogotá | Usme | LOCALITY | 3 |
| Bogotá | Tunjuelito | LOCALITY | 3 |
| Bogotá | Bosa | LOCALITY | 3 |
| Bogotá | Kennedy | LOCALITY | 3 |
| Bogotá | Fontibón | LOCALITY | 3 |
| Bogotá | Engativá | LOCALITY | 3 |
| Bogotá | Suba | LOCALITY | 3 |
| Bogotá | Barrios Unidos | LOCALITY | 3 |
| Bogotá | Teusaquillo | LOCALITY | 3 |
| Bogotá | Los Mártires | LOCALITY | 3 |
| Bogotá | Antonio Nariño | LOCALITY | 3 |
| Bogotá | Puente Aranda | LOCALITY | 3 |
| Bogotá | La Candelaria | LOCALITY | 3 |
| Bogotá | Rafael Uribe Uribe | LOCALITY | 3 |
| Bogotá | Ciudad Bolívar | LOCALITY | 3 |
| Bogotá | Sumapaz | LOCALITY | 3 |

#### Medellín - Comunas

| Ciudad | Nombre | Type | Level |
|--------|--------|------|-------|
| Medellín | Popular | COMMUNE | 3 |
| Medellín | Santa Cruz | COMMUNE | 3 |
| Medellín | Manrique | COMMUNE | 3 |
| Medellín | Aranjuez | COMMUNE | 3 |
| Medellín | Castilla | COMMUNE | 3 |
| Medellín | Doce de Octubre | COMMUNE | 3 |
| Medellín | Robledo | COMMUNE | 3 |
| Medellín | Villa Hermosa | COMMUNE | 3 |
| Medellín | Buenos Aires | COMMUNE | 3 |
| Medellín | La Candelaria | COMMUNE | 3 |
| Medellín | Laureles - Estadio | COMMUNE | 3 |
| Medellín | La América | COMMUNE | 3 |
| Medellín | San Javier | COMMUNE | 3 |
| Medellín | El Poblado | COMMUNE | 3 |
| Medellín | Guayabal | COMMUNE | 3 |
| Medellín | Belén | COMMUNE | 3 |

#### Cali - Comunas

| Ciudad | Nombre | Type | Level |
|--------|--------|------|-------|
| Cali | Comuna 1 | COMMUNE | 3 |
| Cali | Comuna 2 | COMMUNE | 3 |
| Cali | Comuna 3 | COMMUNE | 3 |
| Cali | Comuna 4 | COMMUNE | 3 |
| Cali | Comuna 5 | COMMUNE | 3 |
| Cali | Comuna 6 | COMMUNE | 3 |
| Cali | Comuna 7 | COMMUNE | 3 |
| Cali | Comuna 8 | COMMUNE | 3 |
| Cali | Comuna 9 | COMMUNE | 3 |
| Cali | Comuna 10 | COMMUNE | 3 |
| Cali | Comuna 11 | COMMUNE | 3 |
| Cali | Comuna 12 | COMMUNE | 3 |
| Cali | Comuna 13 | COMMUNE | 3 |
| Cali | Comuna 14 | COMMUNE | 3 |
| Cali | Comuna 15 | COMMUNE | 3 |
| Cali | Comuna 16 | COMMUNE | 3 |
| Cali | Comuna 17 | COMMUNE | 3 |
| Cali | Comuna 18 | COMMUNE | 3 |
| Cali | Comuna 19 | COMMUNE | 3 |
| Cali | Comuna 20 | COMMUNE | 3 |
| Cali | Comuna 21 | COMMUNE | 3 |
| Cali | Comuna 22 | COMMUNE | 3 |

#### Barranquilla - Localidades

| Ciudad | Nombre | Type | Level |
|--------|--------|------|-------|
| Barranquilla | Riomar | LOCALITY | 3 |
| Barranquilla | Norte - Centro Histórico | LOCALITY | 3 |
| Barranquilla | Sur Occidente | LOCALITY | 3 |
| Barranquilla | Metropolitana | LOCALITY | 3 |
| Barranquilla | Sur Oriente | LOCALITY | 3 |

> **Nota:** Se configuran comunas/localidades para las 4 ciudades principales. Se pueden agregar más ciudades posteriormente sin cambios de schema.

---

## Flujos de Entity (CRUD)

Ambas tablas nuevas deben tener su flujo completo de entity, siguiendo el patrón existente del proyecto (ej: `country_router.py`, `CountryController`, etc.).

### Entity: `geo_division_type`

Flujo CRUD estándar registrado en `route.py` (entities):

| Operación | Ruta | Método | Descripción |
|-----------|------|--------|-------------|
| Save | `POST /geo-division-type` | POST | Crear un nuevo tipo de división |
| Update | `PUT /geo-division-type` | PUT | Actualizar un tipo existente |
| List | `POST /geo-division-type/list` | POST | Listar tipos con paginación |
| Read | `GET /geo-division-type/{id}` | GET | Obtener un tipo por ID |
| Delete | `DELETE /geo-division-type/{id}` | DELETE | Eliminar un tipo |

**Archivos del flujo:**
- `src/domain/models/entities/geo_division_type/` - Modelos Pydantic (Save, Update, Read, Delete, index)
- `src/infrastructure/database/entities/geo_division_type_entity.py` - Entity SQLAlchemy
- `src/infrastructure/database/mappers/geo_division_type_mapper.py` - Mapper
- `src/domain/services/repositories/entities/i_geo_division_type_repository.py` - Interfaz
- `src/infrastructure/database/repositories/entities/geo_division_type_repository.py` - Repositorio
- `src/domain/services/use_cases/entities/geo_division_type/` - Use cases CRUD
- `src/infrastructure/web/controller/entities/geo_division_type_controller.py` - Controller
- `src/infrastructure/web/entities_routes/geo_division_type_router.py` - Router

### Entity: `geo_division`

Flujo CRUD estándar registrado en `route.py` (entities):

| Operación | Ruta | Método | Descripción |
|-----------|------|--------|-------------|
| Save | `POST /geo-division` | POST | Crear una nueva división |
| Update | `PUT /geo-division` | PUT | Actualizar una división existente |
| List | `POST /geo-division/list` | POST | Listar divisiones con paginación |
| Read | `GET /geo-division/{id}` | GET | Obtener una división por ID |
| Delete | `DELETE /geo-division/{id}` | DELETE | Eliminar una división |

**Archivos del flujo:**
- `src/domain/models/entities/geo_division/` - Modelos Pydantic (Save, Update, Read, Delete, index)
- `src/infrastructure/database/entities/geo_division_entity.py` - Entity SQLAlchemy
- `src/infrastructure/database/mappers/geo_division_mapper.py` - Mapper
- `src/domain/services/repositories/entities/i_geo_division_repository.py` - Interfaz
- `src/infrastructure/database/repositories/entities/geo_division_repository.py` - Repositorio
- `src/domain/services/use_cases/entities/geo_division/` - Use cases CRUD
- `src/infrastructure/web/controller/entities/geo_division_controller.py` - Controller
- `src/infrastructure/web/entities_routes/geo_division_router.py` - Router

---

## Flujos de Negocio (Endpoints Dinámicos)

Los endpoints de negocio se registran en `route_business.py` a través de un nuevo router `geography_router`. Estos endpoints son **dinámicos** y usan la tabla `geo_division_type` para permitir consultas flexibles por país y tipo.

### Router: `geography_router`

Prefijo: `/geo`

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/geo/countries` | No | Listar todos los países (nodos con level=0). Público para registro de usuarios |
| GET | `/geo/country/{country_id}/types` | No | Listar los tipos de división disponibles para un país. Dinámico: consulta qué tipos tiene configurados ese país |
| GET | `/geo/country/{country_id}/type/{type_name}` | No | Listar divisiones de un país filtradas por tipo (ej: todos los DEPARTMENT de Colombia). `type_name` es el `name` de `geo_division_type` |
| GET | `/geo/{id}/children` | No | Listar hijos directos de una división. Dinámico: funciona para cualquier nivel |
| GET | `/geo/{id}/children/type/{type_name}` | No | Listar hijos de una división filtrados por tipo |
| GET | `/geo/{id}/hierarchy` | No | Obtener jerarquía completa hacia arriba (ej: Comuna > Ciudad > Departamento > País) |
| GET | `/geo/{id}` | No | Obtener detalle de una división específica |

> **Nota:** Estos endpoints son públicos (sin autenticación) porque se usan en el flujo de registro de usuarios externos y creación de compañías.

### Response Models (Pydantic)

#### `GeoDivisionItemResponse`

Modelo base para representar un nodo de la jerarquía. Se usa en la mayoría de los endpoints.

```python
class GeoDivisionItemResponse(BaseModel):
    id: UUID4 = Field(...)
    name: str = Field(...)
    code: Optional[str] = Field(default=None)       # Código DANE/ISO
    phone_code: Optional[str] = Field(default=None)  # Solo para COUNTRY
    level: int = Field(...)
    type: str = Field(...)                           # name del geo_division_type (COUNTRY, DEPARTMENT, etc.)
    type_label: str = Field(...)                     # label del geo_division_type ("País", "Departamento", etc.)
```

**Usado en:** `GET /geo/countries`, `GET /geo/country/{id}/type/{type_name}`, `GET /geo/{id}/children`, `GET /geo/{id}/children/type/{type_name}`, `GET /geo/{id}`

---

#### `GeoDivisionTypeByCountryResponse`

Modelo para el endpoint que retorna los tipos de división disponibles en un país, incluyendo la cantidad de cada tipo.

```python
class GeoDivisionTypeByCountryResponse(BaseModel):
    id: UUID4 = Field(...)                           # ID del geo_division_type
    name: str = Field(...)                           # DEPARTMENT, CITY, COMMUNE, etc.
    label: str = Field(...)                          # "Departamento", "Ciudad", "Comuna", etc.
    level: int = Field(...)                          # Nivel jerárquico (1, 2, 3...)
    count: int = Field(...)                          # Cantidad de divisiones de este tipo en el país
```

**Usado en:** `GET /geo/country/{id}/types`

---

#### `GeoDivisionHierarchyResponse`

Modelo para el endpoint de jerarquía. Retorna una lista ordenada desde el nodo consultado hasta el país (raíz).

```python
class GeoDivisionHierarchyItemResponse(BaseModel):
    id: UUID4 = Field(...)
    name: str = Field(...)
    code: Optional[str] = Field(default=None)
    phone_code: Optional[str] = Field(default=None)
    level: int = Field(...)
    type: str = Field(...)
    type_label: str = Field(...)

class GeoDivisionHierarchyResponse(BaseModel):
    node: GeoDivisionHierarchyItemResponse = Field(...)        # Nodo consultado
    ancestors: List[GeoDivisionHierarchyItemResponse] = Field(...)  # Ancestros ordenados de hijo a raíz
    depth: int = Field(...)                                     # Profundidad total de la jerarquía
```

**Usado en:** `GET /geo/{id}/hierarchy`

---

#### Estructura de archivos de los models

```
src/domain/models/business/geography/
├── geo_division_item_response.py           # GeoDivisionItemResponse
├── geo_division_type_by_country_response.py # GeoDivisionTypeByCountryResponse
├── geo_division_hierarchy_response.py       # GeoDivisionHierarchyResponse, GeoDivisionHierarchyItemResponse
└── index.py                                 # Re-exports
```

---

### Ejemplos de Uso con Response Models

**1. `GET /geo/countries`** → `Response[List[GeoDivisionItemResponse]]`

```json
{
  "data": [
    {
      "id": "a1b2c3d4-...",
      "name": "Colombia",
      "code": "CO",
      "phone_code": "+57",
      "level": 0,
      "type": "COUNTRY",
      "type_label": "País"
    }
  ]
}
```

**2. `GET /geo/country/{colombia_id}/types`** → `Response[List[GeoDivisionTypeByCountryResponse]]`

```json
{
  "data": [
    { "id": "...", "name": "DEPARTMENT", "label": "Departamento", "level": 1, "count": 33 },
    { "id": "...", "name": "CITY", "label": "Ciudad", "level": 2, "count": 43 },
    { "id": "...", "name": "COMMUNE", "label": "Comuna", "level": 3, "count": 38 },
    { "id": "...", "name": "LOCALITY", "label": "Localidad", "level": 3, "count": 25 }
  ]
}
```

**3. `GET /geo/country/{colombia_id}/type/DEPARTMENT`** → `Response[List[GeoDivisionItemResponse]]`

```json
{
  "data": [
    { "id": "...", "name": "Antioquia", "code": "05", "phone_code": null, "level": 1, "type": "DEPARTMENT", "type_label": "Departamento" },
    { "id": "...", "name": "Atlántico", "code": "08", "phone_code": null, "level": 1, "type": "DEPARTMENT", "type_label": "Departamento" }
  ]
}
```

**4. `GET /geo/{antioquia_id}/children`** → `Response[List[GeoDivisionItemResponse]]`

```json
{
  "data": [
    { "id": "...", "name": "Medellín", "code": "05001", "phone_code": null, "level": 2, "type": "CITY", "type_label": "Ciudad" },
    { "id": "...", "name": "Bello", "code": "05088", "phone_code": null, "level": 2, "type": "CITY", "type_label": "Ciudad" },
    { "id": "...", "name": "Envigado", "code": "05266", "phone_code": null, "level": 2, "type": "CITY", "type_label": "Ciudad" }
  ]
}
```

**5. `GET /geo/{medellin_id}/children`** → `Response[List[GeoDivisionItemResponse]]`

```json
{
  "data": [
    { "id": "...", "name": "El Poblado", "code": null, "phone_code": null, "level": 3, "type": "COMMUNE", "type_label": "Comuna" },
    { "id": "...", "name": "Laureles - Estadio", "code": null, "phone_code": null, "level": 3, "type": "COMMUNE", "type_label": "Comuna" },
    { "id": "...", "name": "Belén", "code": null, "phone_code": null, "level": 3, "type": "COMMUNE", "type_label": "Comuna" }
  ]
}
```

**6. `GET /geo/{el_poblado_id}/hierarchy`** → `Response[GeoDivisionHierarchyResponse]`

```json
{
  "data": {
    "node": {
      "id": "...", "name": "El Poblado", "code": null, "phone_code": null,
      "level": 3, "type": "COMMUNE", "type_label": "Comuna"
    },
    "ancestors": [
      { "id": "...", "name": "Medellín", "code": "05001", "phone_code": null, "level": 2, "type": "CITY", "type_label": "Ciudad" },
      { "id": "...", "name": "Antioquia", "code": "05", "phone_code": null, "level": 1, "type": "DEPARTMENT", "type_label": "Departamento" },
      { "id": "...", "name": "Colombia", "code": "CO", "phone_code": "+57", "level": 0, "type": "COUNTRY", "type_label": "País" }
    ],
    "depth": 4
  }
}
```

**7. `GET /geo/{el_poblado_id}`** → `Response[GeoDivisionItemResponse]`

```json
{
  "data": {
    "id": "...",
    "name": "El Poblado",
    "code": null,
    "phone_code": null,
    "level": 3,
    "type": "COMMUNE",
    "type_label": "Comuna"
  }
}
```

---

### Archivos del flujo de negocio

**Archivos a crear:**
- `src/domain/models/business/geography/geo_division_item_response.py`
- `src/domain/models/business/geography/geo_division_type_by_country_response.py`
- `src/domain/models/business/geography/geo_division_hierarchy_response.py`
- `src/domain/models/business/geography/index.py`
- `src/infrastructure/database/repositories/business/geography_repository.py` - Queries dinámicas
- `src/infrastructure/database/repositories/business/mappers/geography/geography_mapper.py` - Mappers entity → response
- `src/domain/models/business/geography/` - Response models (3 + index)
- `src/domain/services/use_cases/business/geography/` - Use cases de negocio (cada uno en su carpeta):
  - `countries/countries_use_case.py` - Listar países
  - `types_by_country/types_by_country_use_case.py` - Tipos disponibles por país
  - `by_country_and_type/by_country_and_type_use_case.py` - Divisiones por país y tipo
  - `children/children_use_case.py` - Hijos directos
  - `children_by_type/children_by_type_use_case.py` - Hijos filtrados por tipo
  - `hierarchy/hierarchy_use_case.py` - Jerarquía completa
  - `detail/detail_use_case.py` - Detalle de un nodo
- `src/infrastructure/web/controller/business/geography_controller.py`
- `src/infrastructure/web/business_routes/geography_router.py`

**Archivos a modificar:**
- `src/infrastructure/web/routes/route_business.py` - Registrar `geography_router`

---

## Fases de Implementación

### Fase 1: Migración de Base de Datos - Nuevas Tablas ✅ COMPLETADA
**Alcance:** Crear tablas `geo_division_type` y `geo_division` con índices

**Archivos de migración:**
- `changelog-v51.sql` ✅ - Crear tabla `geo_division_type` con registros iniciales (12 tipos)
- `changelog-v52.sql` ✅ - Crear tabla `geo_division` con índices

### Fase 2: Migración de Datos - Colombia ✅ COMPLETADA
**Alcance:** Migrar datos de `country` a `geo_division` e insertar departamentos, ciudades y comunas/localidades

**Archivos de migración:**
- `changelog-v53.sql` ✅ - Migrar Colombia de `country` a `geo_division` (preservando UUID original)
- `changelog-v54.sql` ✅ - Insertar departamentos de Colombia (level 1, 33 registros)
- `changelog-v55.sql` ✅ - Insertar ciudades principales de Colombia (level 2, 43 registros)
- `changelog-v56.sql` ✅ - Insertar comunas/localidades (level 3: Bogotá 20, Medellín 16, Cali 22, Barranquilla 5 = 63 registros)

### Fase 3: Migración de FKs y Limpieza de `location` ✅ COMPLETADA
**Alcance:** Redirigir FKs de `country` a `geo_division`, eliminar campo `city`, agregar `city_id` a `location`

**Archivos de migración:**
- `changelog-v57.sql` ✅ - Alterar tabla `location` (redirigir `country_id`, eliminar `city`, agregar `city_id`, agregar `latitude`, `longitude`, `google_place_id`)
- `changelog-v58.sql` ✅ - Alterar tabla `user_country` (redirigir `country_id`)
- `changelog-v59.sql` ✅ - Eliminar tabla `country`

### Fase 4: Flujo de Entity - `geo_division_type` ✅ COMPLETADA
**Alcance:** CRUD completo para `geo_division_type` (entity, modelos, mapper, repositorio, use cases, controller, router)

**Archivos creados:**
- `src/infrastructure/database/entities/geo_division_type_entity.py` ✅
- `src/infrastructure/database/mappers/geo_division_type_mapper.py` ✅
- `src/domain/models/entities/geo_division_type/` ✅ (GeoDivisionType, Save, Update, Read, Delete, index)
- `src/domain/services/repositories/entities/i_geo_division_type_repository.py` ✅
- `src/infrastructure/database/repositories/entities/geo_division_type_repository.py` ✅
- `src/domain/services/use_cases/entities/geo_division_type/` ✅ (CRUD completo + index)
- `src/infrastructure/web/controller/entities/geo_division_type_controller.py` ✅
- `src/infrastructure/web/entities_routes/geo_division_type_router.py` ✅

**Archivos modificados:**
- `src/infrastructure/web/routes/route.py` ✅ - Registrado `geo_division_type_router`

### Fase 5: Flujo de Entity - `geo_division` ✅ COMPLETADA
**Alcance:** CRUD completo para `geo_division` (entity, modelos, mapper, repositorio, use cases, controller, router)

**Archivos creados:**
- `src/infrastructure/database/entities/geo_division_entity.py` ✅
- `src/infrastructure/database/mappers/geo_division_mapper.py` ✅
- `src/domain/models/entities/geo_division/` ✅ (GeoDivision, Save, Update, Read, Delete, index)
- `src/domain/services/repositories/entities/i_geo_division_repository.py` ✅
- `src/infrastructure/database/repositories/entities/geo_division_repository.py` ✅
- `src/domain/services/use_cases/entities/geo_division/` ✅ (CRUD completo + index)
- `src/infrastructure/web/controller/entities/geo_division_controller.py` ✅
- `src/infrastructure/web/entities_routes/geo_division_router.py` ✅

**Archivos modificados:**
- `src/infrastructure/web/routes/route.py` ✅ - Registrado `geo_division_router`

### Fase 6: Flujos de Negocio (Endpoints Dinámicos) ✅ COMPLETADA
**Alcance:** Endpoints de negocio: países, divisiones por tipo y país, hijos, jerarquía

**Archivos creados:**
- `src/domain/models/business/geography/` ✅ - Response models (3 + index)
- `src/infrastructure/database/repositories/business/geography_repository.py` ✅
- `src/infrastructure/database/repositories/business/mappers/geography/geography_mapper.py` ✅
- `src/domain/models/business/geography/` ✅ - Response models (3 + index)
- `src/domain/services/use_cases/business/geography/` ✅ (7 use cases, cada uno en su carpeta)
- `src/infrastructure/web/controller/business/geography_controller.py` ✅
- `src/infrastructure/web/business_routes/geography_router.py` ✅

**Archivos modificados:**
- `src/infrastructure/web/routes/route_business.py` ✅ - Registrado `geography_router`

### Fase 7: Actualizar Entidad Location ✅ COMPLETADA
**Alcance:** Modificar entity, modelos, mapper y lógica de `location`. Incluye nuevos campos de geolocalización (`latitude`, `longitude`, `google_place_id`)

**Archivos modificados:**

| Archivo | Cambio |
|---------|--------|
| `src/infrastructure/database/entities/location_entity.py` ✅ | Eliminado `city`. Agregado `city_id` (UUID, FK). Agregado `latitude` (Numeric(10,8), nullable). Agregado `longitude` (Numeric(11,8), nullable). Agregado `google_place_id` (String(255), nullable) |
| `src/domain/models/entities/location/location.py` ✅ | Eliminado `city: str`. Agregado `city_id: Optional[UUID4]`, `latitude: Optional[Decimal]`, `longitude: Optional[Decimal]`, `google_place_id: Optional[str]` |
| `src/domain/models/entities/location/location_save.py` ✅ | Eliminado `city: str`. Agregado `city_id: Optional[UUID4]`, `latitude: Optional[Decimal]`, `longitude: Optional[Decimal]`, `google_place_id: Optional[str]` |
| `src/domain/models/entities/location/location_update.py` ✅ | Eliminado `city: str`. Agregado `city_id: Optional[UUID4]`, `latitude: Optional[Decimal]`, `longitude: Optional[Decimal]`, `google_place_id: Optional[str]` |
| `src/infrastructure/database/mappers/location_mapper.py` ✅ | Eliminado mapeo de `.city`. Agregado mapeo de `.city_id`, `.latitude`, `.longitude`, `.google_place_id` en: `map_to_location`, `map_to_location_entity`, `map_to_save_location_entity`, `map_to_update_location_entity` |

> **Nota:** La validación de `city_id` como descendiente de `country_id` y rangos de coordenadas se implementará en la Fase 8 junto con la actualización de los flujos existentes.

### Fase 8: Actualizar Flujos Existentes (Migración de `country`) ✅ COMPLETADA
**Alcance:** Actualizar **todo** el código que referenciaba la tabla `country` o el campo `city` de `location`. Total: **47 archivos** de código impactados (18 eliminados, 29 modificados)

#### 8.1 Entities y Mappers ✅

| Archivo | Cambio |
|---------|--------|
| `src/infrastructure/database/entities/user_country_entity.py` ✅ | Actualizado comentario: FK ahora apunta a `geo_division(id)` |
| `src/infrastructure/database/mappers/user_country_mapper.py` ✅ | Comentarios actualizados (la columna `country_id` se mantiene pero apunta a `geo_division`) |

#### 8.2 Login / Refresh Token (Auth Repository y Mappers) ✅

| Archivo | Cambio |
|---------|--------|
| `src/infrastructure/database/repositories/business/auth_repository.py` ✅ | `CountryEntity` → `GeoDivisionEntity` en import, JOINs de `initial_user_data` y `user_country`. Método `user_country` retorna `GeoDivisionEntity` |
| `src/infrastructure/database/repositories/business/mappers/auth/login/login_mapper.py` ✅ | `CountryEntity` → `GeoDivisionEntity` en import. `map_to_country_login_response`: recibe `GeoDivisionEntity`. `map_to_location_login_response`: eliminado `city`, agregado `city_id`, `latitude`, `longitude`, `google_place_id` |

#### 8.3 Login Use Cases ✅

| Archivo | Cambio |
|---------|--------|
| `src/domain/services/use_cases/business/auth/login/auth_login_use_case.py` ✅ | Sin cambios necesarios (no importaba `CountryEntity` directamente) |
| `src/domain/services/use_cases/business/auth/login/auth_login_external_use_case.py` ✅ | Sin cambios necesarios (no importaba `CountryEntity` directamente) |
| `src/domain/services/use_cases/business/auth/login/auth_refresh_token_use_case.py` ✅ | Sin cambios necesarios |
| `src/domain/services/use_cases/business/auth/login/auth_refresh_token_external_use_case.py` ✅ | Sin cambios necesarios |
| `src/domain/services/use_cases/business/auth/login/auth_login_refresh_token_use_case.py` ✅ | Sin cambios necesarios |
| `src/domain/services/use_cases/business/auth/login/auth_initial_user_data_use_case.py` ✅ | Import `CountryEntity` → `GeoDivisionEntity`. Type hint de return tuple actualizado |

#### 8.4 Response Models ✅

| Archivo | Cambio |
|---------|--------|
| `src/domain/models/business/auth/login/auth_login_response.py` ✅ | `LocationLoginResponse`: eliminado `city: str`, agregado `city_id: Optional[UUID4]`, `latitude: Optional[Decimal]`, `longitude: Optional[Decimal]`, `google_place_id: Optional[str]`. `CountryLoginResponse` mantuvo estructura (campos compatibles con `GeoDivisionEntity`). Import de `Decimal` agregado |

#### 8.5 Create Company ✅

| Archivo | Cambio |
|---------|--------|
| `src/domain/services/use_cases/business/auth/create_company/create_company_use_case.py` ✅ | `CountryRead` → `GeoDivisionRead`. `CountryRepository` → `GeoDivisionRepository`. `CountryReadUseCase` → `GeoDivisionReadUseCase`. `LocationSave`: eliminado `city`, agregado `city_id`, `latitude`, `longitude`, `google_place_id` |
| `src/domain/models/business/auth/create_company/create_company_request.py` ✅ | `LocationData`: eliminado `city: str`, agregado `city_id: Optional[UUID4]`, `latitude: Optional[Decimal]`, `longitude: Optional[Decimal]`, `google_place_id: Optional[str]`. Ejemplos actualizados |

#### 8.6 Create/Delete User External ✅

| Archivo | Cambio |
|---------|--------|
| `src/domain/services/use_cases/business/auth/create_user_external/create_user_external_use_case.py` ✅ | `CountryRead` → `GeoDivisionRead`. `CountryReadUseCase` → `GeoDivisionReadUseCase`. `CountryRepository` → `GeoDivisionRepository` |
| `src/domain/models/business/auth/create_user_external/create_user_external_request.py` ✅ | Actualizada doc: `country_id` ahora es FK a `geo_division(id)` tipo COUNTRY |
| `src/domain/services/use_cases/business/auth/delete_user_external/delete_user_external_use_case.py` ✅ | Sin cambios necesarios (`UserCountryRepository` sin imports a `CountryEntity`) |

#### 8.7 Rutas y Registros ✅

| Archivo | Cambio |
|---------|--------|
| `src/infrastructure/web/routes/route.py` ✅ | Eliminado import y registro de `country_router` |

#### 8.8 Archivos ELIMINADOS (18 archivos) ✅

| Archivo | Razón |
|---------|-------|
| `src/infrastructure/database/entities/country_entity.py` ✅ | Entity reemplazada por `GeoDivisionEntity` |
| `src/infrastructure/database/mappers/country_mapper.py` ✅ | Mapper reemplazado por `geo_division_mapper.py` |
| `src/domain/models/entities/country/country.py` ✅ | Modelo reemplazado |
| `src/domain/models/entities/country/country_read.py` ✅ | Modelo reemplazado |
| `src/domain/models/entities/country/country_save.py` ✅ | Modelo reemplazado |
| `src/domain/models/entities/country/country_update.py` ✅ | Modelo reemplazado |
| `src/domain/models/entities/country/country_delete.py` ✅ | Modelo reemplazado |
| `src/domain/models/entities/country/index.py` ✅ | Index reemplazado |
| `src/domain/services/repositories/entities/i_country_repository.py` ✅ | Interfaz reemplazada |
| `src/infrastructure/database/repositories/entities/country_repository.py` ✅ | Repositorio reemplazado |
| `src/domain/services/use_cases/entities/country/country_read_use_case.py` ✅ | Use case reemplazado |
| `src/domain/services/use_cases/entities/country/country_save_use_case.py` ✅ | Use case reemplazado |
| `src/domain/services/use_cases/entities/country/country_update_use_case.py` ✅ | Use case reemplazado |
| `src/domain/services/use_cases/entities/country/country_delete_use_case.py` ✅ | Use case reemplazado |
| `src/domain/services/use_cases/entities/country/country_list_use_case.py` ✅ | Use case reemplazado |
| `src/domain/services/use_cases/entities/country/index.py` ✅ | Index reemplazado |
| `src/infrastructure/web/controller/entities/country_controller.py` ✅ | Controller reemplazado |
| `src/infrastructure/web/entities_routes/country_router.py` ✅ | Router reemplazado |

> **Verificación de integridad:** Se confirmó con búsqueda global que no quedan imports a `country_entity.py`, `country_repository.py`, `CountryReadUseCase`, ni ningún otro archivo eliminado en todo el codebase Python.

### Fase 9: Actualizar Documentación de Flujos ✅ COMPLETADA
**Alcance:** Actualizar los 3 documentos de flujos que referencian `country`, `city` o `CountryEntity`

| Documento | Secciones Impactadas | Cambios | Estado |
|-----------|---------------------|---------|--------|
| `docs/07-flows/07-00-flows-overview.md` ✅ | ~3 secciones | `CountryReadUseCase` → `GeoDivisionReadUseCase` en Create Company. Ejemplo de request: `city` → `city_id`. Versión actualizada a 1.8. Historial de cambios actualizado | ✅ |
| `docs/07-flows/07-05-create-company-flow.md` ✅ | **~18 secciones** (más impactado) | Diagrama de flujo: `city` → `city_id`. Validación "Country existe?" → "GeoDivision existe y es tipo COUNTRY?". Arquitectura: `CountryReadUseCase` → `GeoDivisionReadUseCase`. `CountryRepository` → `GeoDivisionRepository`. Modelo `LocationData`: eliminado `city: str`, agregado `city_id: Optional[UUID4]`, `latitude`, `longitude`, `google_place_id`. `LocationSave`: `city` → `city_id` + nuevos campos. Request examples actualizados. Import `GeoDivisionRead` agregado. Tablas de BD: agregado `geo_division` y `geo_division_type`. Versión actualizada a 1.1. Historial de cambios actualizado | ✅ |
| `docs/07-flows/07-12-login-flow.md` ✅ | ~10 secciones | Response example: `city` → `city_id`, agregado `latitude`, `longitude`, `google_place_id`. `user_country` FK: `country(id)` → `geo_division(id)`. Entity: `ForeignKey("country.id")` → comentario FK a `geo_division(id)`. Relationship: `CountryEntity` → `GeoDivisionEntity`. Diagrama ER: `COUNTRY` → `GEO_DIVISION (COUNTRY)`. Query JOIN docs actualizados. Versión actualizada a 2.6. Historial de cambios actualizado | ✅ |

### Fase 10: Testing y QA ⏳ PENDIENTE (futuro)
**Alcance:** Pruebas de integridad y regresión
**Estado:** Pendiente para implementación futura

> **Nota:** La verificación de integridad del codebase (no quedan imports a `CountryEntity`, `country_mapper`, `country_repository`) ya fue realizada exitosamente como parte de la Fase 8. Las pruebas formales con pytest se implementarán en una fase futura.

- [ ] Validar que la jerarquía es consistente (un nodo hijo siempre tiene un padre válido)
- [ ] Validar que `level` es coherente con la profundidad real
- [ ] Validar que `location.country_id` apunta a un nodo de tipo COUNTRY
- [ ] Validar que `location.city_id` apunta a un nodo de tipo CITY
- [ ] Validar que `city_id` es descendiente de `country_id` en la jerarquía
- [ ] Validar endpoints dinámicos: `/geo/country/{id}/types` retorna tipos correctos
- [ ] Pruebas de regresión en login (interno y externo)
- [ ] Pruebas de regresión en creación de company/location
- [ ] Pruebas de regresión en registro de usuario externo
- [ ] Pruebas de regresión en creación de usuario externo con `country_id`
- [ ] Pruebas de performance con consultas jerárquicas
- [x] Verificar que no quedan imports a `CountryEntity`, `country_mapper`, `country_repository` en todo el codebase (✅ verificado en Fase 8)

---

## Diagrama ER

```
┌─────────────────────┐
│  geo_division_type   │
├─────────────────────┤
│ id (PK)             │
│ name (UNIQUE)       │◄──────────────────────┐
│ label               │                       │
│ description         │                       │
│ state               │                       │
│ created_date        │                       │
│ updated_date        │                       │
└─────────────────────┘                       │
                                              │
                          ┌───────────────────┤
                          │   geo_division     │
                          ├───────────────────┤
                     ┌───►│ id (PK)           │
                     │    │ top_id (FK) ──────┤──┐ (self-reference)
                     │    │ geo_division_type_id│ │
                     │    │ name              │  │
                     │    │ code              │  │
                     │    │ phone_code        │  │
                     │    │ level             │  │
                     │    │ state             │  │
                     │    │ created_date      │  │
                     │    │ updated_date      │  │
                     │    └───────────────────┘◄─┘
                     │              ▲         ▲
                     │              │         │
           ┌─────────┴──────┐      │    ┌────┴────────────────┐
           │  user_country   │      │    │     location        │
           ├────────────────┤      │    ├─────────────────────┤
           │ id (PK)        │      │    │ id (PK)             │
           │ user_id (FK)   │      │    │ company_id (FK)     │
           │ country_id (FK)┤──────┘    │ country_id (FK) ────┤── geo_division (COUNTRY)
           │ state          │           │ city_id (FK) ───────┤── geo_division (CITY)
           │ created_date   │           │ name                │
           │ updated_date   │           │ address             │
           └────────────────┘           │ phone               │
                                        │ email               │
                                        │ main_location       │
                                        │ state               │
                                        └─────────────────────┘
```

### Jerarquía Recursiva (Ejemplo Colombia)

```
geo_division: Colombia (type: COUNTRY, level: 0, top_id: NULL, code: CO, phone_code: +57)
│
├── geo_division: Antioquia (type: DEPARTMENT, level: 1, code: 05)
│   ├── geo_division: Medellín (type: CITY, level: 2, code: 05001)
│   │   ├── geo_division: El Poblado (type: COMMUNE, level: 3)
│   │   ├── geo_division: Laureles - Estadio (type: COMMUNE, level: 3)
│   │   └── geo_division: Belén (type: COMMUNE, level: 3)
│   ├── geo_division: Bello (type: CITY, level: 2, code: 05088)
│   └── geo_division: Envigado (type: CITY, level: 2, code: 05266)
│
├── geo_division: Bogotá D.C. (type: DEPARTMENT, level: 1, code: 11)
│   └── geo_division: Bogotá (type: CITY, level: 2, code: 11001)
│       ├── geo_division: Usaquén (type: LOCALITY, level: 3)
│       ├── geo_division: Chapinero (type: LOCALITY, level: 3)
│       └── geo_division: Suba (type: LOCALITY, level: 3)
│
└── geo_division: Valle del Cauca (type: DEPARTMENT, level: 1, code: 76)
    ├── geo_division: Cali (type: CITY, level: 2, code: 76001)
    │   ├── geo_division: Comuna 17 (type: COMMUNE, level: 3)
    │   └── geo_division: Comuna 22 (type: COMMUNE, level: 3)
    └── geo_division: Palmira (type: CITY, level: 2, code: 76520)
```

---

## Consideraciones

### Rendimiento
- Las consultas recursivas (CTE) en PostgreSQL son eficientes para jerarquías de 3-4 niveles
- El índice compuesto `(top_id, geo_division_type_id)` optimiza la consulta más frecuente: "hijos de un nodo filtrados por tipo"
- El campo `level` evita tener que calcular la profundidad dinámicamente
- `GET /countries` es simplemente `SELECT * FROM geo_division WHERE level = 0`
- El endpoint `/country/{id}/types` usa un `SELECT DISTINCT` + `COUNT` sobre `geo_division_type_id` filtrado por los descendientes del país

### Integridad de Datos
- `ON DELETE RESTRICT` en `top_id`: no se puede eliminar un nodo padre si tiene hijos
- `ON DELETE RESTRICT` en `geo_division_type_id`: no se puede eliminar un tipo si hay divisiones usándolo
- `ON DELETE RESTRICT` en `location.country_id` y `location.city_id`: no se puede eliminar una división si hay sedes asociadas
- Validación en use case de `save` de `geo_division`: el `level` debe ser `parent.level + 1`

### Escalabilidad
- La estructura soporta cualquier profundidad de jerarquía
- Nuevos países se agregan como nodos raíz (INSERT), sin cambios en schema
- Nuevos tipos de división se agregan a `geo_division_type` (INSERT), sin migración
- Nuevos niveles jerárquicos por país solo requieren INSERT de datos
- Los endpoints de negocio son completamente dinámicos: no hay lógica hardcodeada por país

### Migración de la tabla `country`
- **Paso crítico:** Al migrar Colombia de `country` a `geo_division`, se debe preservar el UUID original
- Se debe verificar que no existan registros huérfanos antes de eliminar `country`
- Se eliminan todos los archivos del flujo entity de `country` (entity, mapper, models, repository, use cases, controller, router)

---

## Historial de Cambios

| Versión | Fecha | Descripción |
|---------|-------|-------------|
| 1.0 | Enero 2026 | Versión inicial del documento |
| 2.0 | Enero 2026 | Rediseño: tabla `geo_division_type`, absorción de `country` en `geo_division`, `location` con `country_id` y `city_id` apuntando a `geo_division` |
| 3.0 | Enero 2026 | Eliminación del campo `city` en `location` (no en producción). Nivel 3: Comunas/Localidades para Bogotá, Medellín, Cali y Barranquilla. Flujos de entity CRUD para ambas tablas nuevas. Endpoints de negocio dinámicos basados en tipos por país |
| 3.1 | Enero 2026 | Auditoría completa de impacto: 47 archivos de código + 3 documentos de flujos. Fase 7 ampliada con modelos y mapper de location. Fase 8 desglosada en 8 sub-secciones con detalle archivo por archivo. Nueva Fase 9 para actualizar documentación de flujos. Fase de Testing renumerada a 10 |
| 3.2 | Enero 2026 | Campos de geolocalización en `location`: `latitude DECIMAL(10,8)`, `longitude DECIMAL(11,8)`, `google_place_id VARCHAR(255)`. Todos nullable para implementación futura. CHECK constraints para rangos válidos. Índice parcial para coordenadas. Response models de negocio definidos con estructura Pydantic completa |
| 3.3 | Enero 2026 | Impacto completo en flujo entity de Location y consumidores: `LocationLoginResponse`, `login_mapper`, `create_company_request`, `create_company_use_case` ahora incluyen `city_id`, `latitude`, `longitude`, `google_place_id`. Documentación de flujos (07-05, 07-12) actualizada para reflejar nuevos campos |
| 3.4 | Enero 2026 | Fase 8 completada: Migración completa de `country` a `geo_division`. 18 archivos eliminados (entity, mapper, models, repository, use cases, controller, router). Todos los imports y JOINs actualizados a `GeoDivisionEntity`. Response models actualizados. `create_company` y `create_user_external` usan `GeoDivisionReadUseCase`. `route.py` sin `country_router` |
| 3.5 | Enero 2026 | Fase 9 completada: Actualización de 3 documentos de flujos. `07-00-flows-overview.md` v1.8: refs a `GeoDivisionReadUseCase`, ejemplos con `city_id`. `07-05-create-company-flow.md` v1.1: ~18 secciones actualizadas (modelos, imports, repos, validaciones, diagramas, ejemplos). `07-12-login-flow.md` v2.6: response con nuevos campos de location, `user_country` FK a `geo_division`, entity docs actualizados |
| 3.6 | Enero 2026 | Fase 10 marcada como pendiente para implementación futura. Verificación de integridad del codebase confirmada (0 referencias residuales a `CountryEntity`, `country_mapper`, `country_repository`). Implementación de Fases 1-9 finalizada |

# 07-15: Migracion de Menus Raiz (/apps y /citas) - Reestructuracion Jerarquica

## Informacion del Documento

| Campo | Detalle |
|-------|---------|
| **Version** | 1.5 |
| **Fecha** | Febrero 13, 2026 |
| **Estado** | Especificado |
| **Autor(es)** | Equipo de Desarrollo Goluti |
| **Responsable** | [Nombre del lider tecnico] |

---

## Tabla de Contenidos

1. [Introduccion](#introduccion)
2. [Objetivo](#objetivo)
3. [Estado Actual](#estado-actual)
4. [Estado Deseado](#estado-deseado)
5. [Cadena de Permisos](#cadena-de-permisos)
6. [Estrategia de Migracion](#estrategia-de-migracion)
7. [Script SQL de Migracion](#script-sql-de-migracion)
8. [Impacto en Flujos Existentes](#impacto-en-flujos-existentes)
9. [Impacto en Codigo](#impacto-en-codigo)
10. [Plan de Ejecucion](#plan-de-ejecucion)
11. [Validaciones Post-Migracion](#validaciones-post-migracion)
12. [Rollback](#rollback)
13. [Riesgos](#riesgos)
14. [Referencias](#referencias)
15. [Historial de Cambios](#historial-de-cambios)

---

## Introduccion

### Problema que Resuelve

Actualmente en la tabla `menu`, todos los items con `company_id = NULL` (templates globales) son nodos raiz independientes (`id == top_id`). No existe un **menu principal contenedor** que los agrupe bajo una jerarquia comun.

Se requiere crear dos nuevos items de menu raiz:
1. **`/apps`**: Pantalla de seleccion de aplicaciones (nodo hoja, sin hijos)
2. **`/citas`**: Menu padre que contiene (gobierna) todos los items existentes con `company_id = NULL`, sin importar si son de tipo `INTERNAL` o `EXTERNAL`

Ambos son nodos raiz independientes (`id == top_id`), de tipo `INTERNAL`, con su cadena completa de permisos.

### Complejidad

Esta migracion es **compleja** porque:

1. **Afecta templates globales**: Los menus con `company_id = NULL` son la plantilla base que se clona al crear cada nueva compania.
2. **Afecta companias existentes**: Las companias ya creadas tienen copias clonadas de estos menus que tambien necesitan el nuevo padre.
3. **Requiere cadena completa de permisos**: Se debe crear un `permission` nuevo, asociarlo al menu via `menu_permission`, y vincularlo a los roles ADMIN y COLLA via `rol_permission`.
4. **Impacta el flujo de login**: La jerarquia de menus se retorna en la respuesta de login (tanto INTERNAL como EXTERNAL).
5. **Impacta la clonacion de menus**: El flujo de create-company clona menus template y debe incluir el nuevo padre.

### Consideraciones Tecnicas

- **UUID**: La tabla `menu` usa `uuid_generate_v4()` como `server_default`. Los modelos de dominio (`Menu`, `MenuSave`) usan `UUID4` de Pydantic. La migracion debe generar UUIDs v4 validos.
- **Enum MENU_TYPE**: Existe la clase `MENU_TYPE` en `src/core/enums/menu_type.py` con valores `INTERNAL` y `EXTERNAL`. El spec referencia estos valores usando el enum.
- **Enum ROL_TYPE**: Existe la clase `ROL_TYPE` en `src/core/enums/rol_type.py` con valores `ADMIN`, `COLLA` y `USER`.

---

## Objetivo

1. Crear un nuevo item de menu `/apps` como **pantalla de aplicaciones** en los templates (`company_id = NULL`)
2. Crear un nuevo item de menu `/citas` como **menu padre principal** en los templates (`company_id = NULL`)
3. Crear un `permission` para cada menu nuevo (template con `company_id = NULL`)
4. Crear las relaciones `menu_permission` entre cada menu y su permiso
5. Crear las relaciones `rol_permission` para los roles **ADMIN** y **COLLA** con ambos permisos
6. Reasignar todos los items existentes con `company_id = NULL` para que su `top_id` apunte a `/citas` (excluyendo `/apps`)
7. Replicar la misma estructura en **todas las companias existentes** (menu, menu_permission)
8. Garantizar que el flujo de **create-company** siga funcionando correctamente
9. Garantizar que el flujo de **login** retorne ambos nodos raiz (`/apps` y `/citas`)

### Alcance

**En alcance:**
- Creacion del menu `/apps` (nodo hoja) en templates globales (`company_id = NULL`)
- Creacion del menu padre `/citas` en templates globales (`company_id = NULL`)
- Creacion de los permisos asociados en tabla `permission` (`apps_access`, `citas_access`)
- Creacion de las relaciones `menu_permission` para ambos menus
- Creacion de las relaciones `rol_permission` para ADMIN y COLLA con ambos permisos
- Reasignacion de `top_id` de items raiz existentes bajo `/citas` (excluyendo `/apps`)
- Replicacion completa en cada compania existente
- Validacion de integridad post-migracion
- Script SQL reversible (rollback)

**Fuera de alcance:**
- Cambios en la estructura de columnas de las tablas
- Nuevos endpoints de API
- Cambios en los modelos de dominio

---

## Estado Actual

### Estructura Actual de Menus Template (`company_id = NULL`)

```
menu (company_id = NULL)
├── Item A (id=A, top_id=A, type=INTERNAL)   ← nodo raiz
├── Item B (id=B, top_id=B, type=INTERNAL)   ← nodo raiz
├── Item C (id=C, top_id=B, type=INTERNAL)   ← hijo de B
├── Item D (id=D, top_id=D, type=EXTERNAL)   ← nodo raiz
└── Item E (id=E, top_id=D, type=EXTERNAL)   ← hijo de D
```

**Problema:** Items A, B y D son raices independientes. No hay un contenedor comun.

### Estructura Actual de Menus por Compania

```
menu (company_id = {company_uuid})
├── Item A' (id=A', top_id=A', type=INTERNAL)  ← clonado de A
├── Item B' (id=B', top_id=B', type=INTERNAL)  ← clonado de B
├── Item C' (id=C', top_id=B', type=INTERNAL)  ← clonado de C (hijo de B')
```

> **Nota**: Solo items `type = INTERNAL` (ver `MENU_TYPE.INTERNAL`) son clonados por el flujo de create-company. Items `type = EXTERNAL` (`MENU_TYPE.EXTERNAL`) son globales y no se clonan por compania.

### Cadena de Permisos Actual

```
rol (ADMIN/COLLA — globales con company_id = NULL, compartidos por todas las companias)
  └── rol_permission (rol_id → permission_id)
        └── permission (company_id = NULL para templates)
              └── menu_permission (permission_id → menu_id)
                    └── menu (company_id = NULL para templates)
```

Cada menu template tiene:
- Un `permission` asociado (con `company_id = NULL`)
- Un `menu_permission` que liga menu ↔ permission
- Uno o mas `rol_permission` que liga permission ↔ rol (ADMIN, COLLA)

> **Nota**: Los roles ADMIN y COLLA actualmente son **globales** (`company_id = NULL`) y compartidos por todas las companias. La tabla `rol` permite roles por compania pero actualmente no se usan de esa forma.

---

## Estado Deseado

### Estructura Deseada de Menus Template (`company_id = NULL`)

```
menu (company_id = NULL)
├── /apps  (id=APPS, top_id=APPS, type=INTERNAL, company_id=NULL)    ← NUEVO - Nodo hoja (sin hijos)
└── /citas (id=CITAS, top_id=CITAS, type=INTERNAL, company_id=NULL)  ← NUEVO PADRE
    ├── Item A (id=A, top_id=CITAS, type=INTERNAL)   ← reasignado
    ├── Item B (id=B, top_id=CITAS, type=INTERNAL)   ← reasignado
    │   └── Item C (id=C, top_id=B, type=INTERNAL)   ← SIN CAMBIO (ya era hijo de B)
    ├── Item D (id=D, top_id=CITAS, type=EXTERNAL)   ← reasignado
    │   └── Item E (id=E, top_id=D, type=EXTERNAL)   ← SIN CAMBIO (ya era hijo de D)
    └── ... todos los demas items raiz
```

> **Nota**: `/apps` y `/citas` son **nodos raiz independientes** (ambos con `id == top_id`). Los items existentes se reasignan SOLO bajo `/citas`. `/apps` es un nodo hoja sin hijos.

### Cadena de Permisos Deseada

```
rol ADMIN ──→ rol_permission ──→ permission "apps_access"  ──→ menu_permission ──→ menu /apps
rol COLLA ──→ rol_permission ──→ permission "apps_access"  ──→ menu_permission ──→ menu /apps

rol ADMIN ──→ rol_permission ──→ permission "citas_access" ──→ menu_permission ──→ menu /citas
rol COLLA ──→ rol_permission ──→ permission "citas_access" ──→ menu_permission ──→ menu /citas
```

### Estructura Deseada de Menus por Compania

```
menu (company_id = {company_uuid})
├── /apps  (id=APPS', top_id=APPS', type=INTERNAL)    ← NUEVO - Nodo hoja
└── /citas (id=CITAS', top_id=CITAS', type=INTERNAL)  ← NUEVO PADRE
    ├── Item A' (id=A', top_id=CITAS', type=INTERNAL)  ← reasignado
    ├── Item B' (id=B', top_id=CITAS', type=INTERNAL)  ← reasignado
    │   └── Item C' (id=C', top_id=B', type=INTERNAL)  ← SIN CAMBIO
    └── ... todos los demas items raiz de esta compania
```

Cada compania existente tendra:
- Su propio menu `/apps` (con `company_id` de la compania)
- Su propio menu `/citas` (con `company_id` de la compania)
- Sus propios `menu_permission` ligando cada menu al permission template correspondiente (`company_id = NULL`)
- Los `rol_permission` son globales (Fase 1), no se necesitan por compania

### Reglas de Reasignacion

| Condicion | Accion |
|-----------|--------|
| `id == top_id` (nodo raiz) y NO es `/apps` ni `/citas` | Cambiar `top_id` al padre `/citas` |
| `id != top_id` (nodo hijo) | **No cambiar** - ya tiene padre correcto |
| `/apps` y `/citas` | Permanecen como nodos raiz (`id == top_id`) |

---

## Cadena de Permisos

### Tablas Involucradas

| Tabla | Columnas Clave | Descripcion |
|-------|---------------|-------------|
| `permission` | `id`, `company_id`, `name`, `description`, `state` | Permisos del sistema. `company_id = NULL` para templates |
| `menu_permission` | `id`, `menu_id`, `permission_id`, `state` | Liga menu ↔ permission |
| `rol_permission` | `id`, `rol_id`, `permission_id`, `state` | Liga rol ↔ permission |
| `rol` | `id`, `company_id`, `name`, `code`, `state` | Roles. `code` usa `ROL_TYPE` enum (ADMIN, COLLA, USER) |

### Flujo de Clonacion Existente (Create Company)

Cuando se crea una compania:

1. **`CloneMenusForCompanyUseCase`**: Clona menus template (`company_id = NULL`, `type = INTERNAL`) → nuevos menus con `company_id = nueva_compania`
2. **`CloneMenuPermissionsForCompanyUseCase`**: Para cada menu clonado, busca los `menu_permission` del menu template original y crea nuevos `menu_permission` con el `menu_id` clonado pero **el mismo `permission_id`** del template

> **Nota critica**: El flujo actual de create-company **NO clona permissions ni rol_permissions**. Solo clona `menu` y `menu_permission`. Los `permission` y `rol` template (con `company_id = NULL`) se reutilizan directamente por todas las companias. Esto significa que en la migracion:
> - Para **templates**: Se crea permission + menu_permission + rol_permission (todo con `company_id = NULL`)
> - Para **companias existentes**: Se crea menu + menu_permission (apuntando al **mismo** permission template)

---

## Estrategia de Migracion

### Enfoque: Migracion en 3 Fases

#### Fase 1: Permissions y Roles Template

1. Crear `permission` "apps_access" con `company_id = NULL`
2. Crear `permission` "citas_access" con `company_id = NULL`
3. Crear `rol_permission` ligando ambos permisos al rol ADMIN (`code = 'ADMIN'`)
4. Crear `rol_permission` ligando ambos permisos al rol COLLA (`code = 'COLLA'`)

> **Nota**: Los roles ADMIN y COLLA son **globales** (`company_id = NULL`) y compartidos por todas las companias. La tabla `rol` permite roles por compania pero actualmente todos los roles registrados tienen `company_id = NULL`.

#### Fase 2: Menus Template y Jerarquia

1. Insertar nuevo menu `/apps` con `company_id = NULL`, `type = 'INTERNAL'` (nodo hoja)
2. Insertar nuevo menu `/citas` con `company_id = NULL`, `type = 'INTERNAL'`
3. Crear `menu_permission` ligando menu `/apps` con permission "apps_access"
4. Crear `menu_permission` ligando menu `/citas` con permission "citas_access"
5. Actualizar `top_id` de todos los items raiz (`id == top_id`) para que apunten a `/citas`, **excluyendo** `/apps` y `/citas`

#### Fase 3: Companias Existentes - Menu y Jerarquia

Para **cada compania activa** (consultando directamente la tabla `company`):

1. Insertar nuevo menu `/apps` con `company_id = {company_id}` (nodo hoja)
2. Insertar nuevo menu `/citas` con `company_id = {company_id}`
3. Crear `menu_permission` ligando `/apps` de la compania con permission template "apps_access"
4. Crear `menu_permission` ligando `/citas` de la compania con permission template "citas_access"
5. Actualizar `top_id` de items raiz de esa compania para que apunten a `/citas`, **excluyendo** `/apps` y `/citas`

> **Nota**: No se requiere crear `rol_permission` por compania. Los roles ADMIN/COLLA son globales (`company_id = NULL`) y sus `rol_permission` ya fueron creados en la Fase 1.

#### Post-Migracion: Validacion

1. Verificar integridad de jerarquia
2. Verificar cadena completa de permisos para ambos menus raiz

---

## Script SQL de Migracion

> **Nota**: Este script debe ser ejecutado manualmente en la base de datos por el usuario. Sigue el formato Liquibase establecido en el proyecto (`-- liquibase formatted sql`, `-- changeset`). Rollback en comentarios `--ROLLBACK`.

### Archivo: `migrations/changelog-v60.sql`

```sql
-- liquibase formatted sql
-- changeset add-apps-citas-root-menus:1739318400000-60

-- ============================================
-- MIGRACION: Agregar menus raiz /apps y /citas
--
-- Crea dos nodos raiz independientes:
-- 1. /apps  - Pantalla de seleccion de aplicaciones (nodo hoja)
-- 2. /citas - Menu padre que gobierna todos los items existentes
--
-- Ambos son INTERNAL, con permisos para ADMIN y COLLA.
-- Items raiz existentes se reasignan bajo /citas.
--
-- UUIDs fijos para templates:
-- Menu /apps:        f6c9d3e4-5a7b-4f8c-bc2d-3e4f5a6b7c8d
-- Permission /apps:  a7d0e4f5-6b8c-4a9d-cd3e-4f5a6b7c8d9e
-- Menu /citas:       d4a8f1b2-7c3e-4d5f-9a6b-1e2f3c4d5e6f
-- Permission /citas: e5b9a2c3-8d4f-4e6a-ab7c-2f3a4d5e6f70
--
-- Tablas afectadas:
-- 1. permission (INSERT x2)
-- 2. rol_permission (INSERT x4)
-- 3. menu (INSERT x2 templates + INSERT x2 por compania + UPDATE top_id)
-- 4. menu_permission (INSERT x2 templates + INSERT x2 por compania)
-- ============================================


-- ============================================
-- FASE 1: PERMISSIONS Y ROLES TEMPLATE
-- ============================================

-- 1.1 Crear permission para /apps
INSERT INTO permission (id, company_id, name, description, state, created_date, updated_date)
VALUES (
    'a7d0e4f5-6b8c-4a9d-cd3e-4f5a6b7c8d9e',
    NULL,
    'apps_access',
    'Permiso de acceso a la pantalla de aplicaciones',
    TRUE,
    NOW(),
    NOW()
);

-- 1.2 Crear permission para /citas
INSERT INTO permission (id, company_id, name, description, state, created_date, updated_date)
VALUES (
    'e5b9a2c3-8d4f-4e6a-ab7c-2f3a4d5e6f70',
    NULL,
    'citas_access',
    'Permiso de acceso al modulo principal de citas',
    TRUE,
    NOW(),
    NOW()
);

-- 1.3 rol_permission: ADMIN + apps_access
INSERT INTO rol_permission (id, rol_id, permission_id, state, created_date, updated_date)
SELECT
    uuid_generate_v4(),
    r.id,
    'a7d0e4f5-6b8c-4a9d-cd3e-4f5a6b7c8d9e',
    TRUE,
    NOW(),
    NOW()
FROM rol r
WHERE r.code = 'ADMIN' AND r.state = true;

-- 1.4 rol_permission: ADMIN + citas_access
INSERT INTO rol_permission (id, rol_id, permission_id, state, created_date, updated_date)
SELECT
    uuid_generate_v4(),
    r.id,
    'e5b9a2c3-8d4f-4e6a-ab7c-2f3a4d5e6f70',
    TRUE,
    NOW(),
    NOW()
FROM rol r
WHERE r.code = 'ADMIN' AND r.state = true;

-- 1.5 rol_permission: COLLA + apps_access
INSERT INTO rol_permission (id, rol_id, permission_id, state, created_date, updated_date)
SELECT
    uuid_generate_v4(),
    r.id,
    'a7d0e4f5-6b8c-4a9d-cd3e-4f5a6b7c8d9e',
    TRUE,
    NOW(),
    NOW()
FROM rol r
WHERE r.code = 'COLLA' AND r.state = true;

-- 1.6 rol_permission: COLLA + citas_access
INSERT INTO rol_permission (id, rol_id, permission_id, state, created_date, updated_date)
SELECT
    uuid_generate_v4(),
    r.id,
    'e5b9a2c3-8d4f-4e6a-ab7c-2f3a4d5e6f70',
    TRUE,
    NOW(),
    NOW()
FROM rol r
WHERE r.code = 'COLLA' AND r.state = true;


-- ============================================
-- FASE 2: MENUS TEMPLATE Y JERARQUIA
-- ============================================

-- 2.1 Insertar menu /apps template (nodo hoja)
INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, type, created_date, updated_date)
VALUES (
    'f6c9d3e4-5a7b-4f8c-bc2d-3e4f5a6b7c8d',
    NULL,
    'apps',
    'Aplicaciones',
    'Pantalla de seleccion de aplicaciones',
    'f6c9d3e4-5a7b-4f8c-bc2d-3e4f5a6b7c8d',     -- Nodo raiz: top_id = id
    '/apps',
    TRUE,
    'grid',
    'INTERNAL',
    NOW(),
    NOW()
);

-- 2.2 Insertar menu /citas template (menu padre)
INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, type, created_date, updated_date)
VALUES (
    'd4a8f1b2-7c3e-4d5f-9a6b-1e2f3c4d5e6f',
    NULL,
    'citas',
    'Citas',
    'Menu principal - Modulo de citas',
    'd4a8f1b2-7c3e-4d5f-9a6b-1e2f3c4d5e6f',     -- Nodo raiz: top_id = id
    '/citas',
    TRUE,
    'calendar',
    'INTERNAL',
    NOW(),
    NOW()
);

-- 2.3 menu_permission para /apps template
INSERT INTO menu_permission (id, menu_id, permission_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),
    'f6c9d3e4-5a7b-4f8c-bc2d-3e4f5a6b7c8d',     -- menu: /apps
    'a7d0e4f5-6b8c-4a9d-cd3e-4f5a6b7c8d9e',     -- permission: apps_access
    TRUE,
    NOW(),
    NOW()
);

-- 2.4 menu_permission para /citas template
INSERT INTO menu_permission (id, menu_id, permission_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),
    'd4a8f1b2-7c3e-4d5f-9a6b-1e2f3c4d5e6f',     -- menu: /citas
    'e5b9a2c3-8d4f-4e6a-ab7c-2f3a4d5e6f70',     -- permission: citas_access
    TRUE,
    NOW(),
    NOW()
);

-- 2.5 Reasignar top_id de items raiz template a /citas
-- Solo afecta nodos raiz (id = top_id), excluyendo /apps y /citas
UPDATE menu
SET top_id = 'd4a8f1b2-7c3e-4d5f-9a6b-1e2f3c4d5e6f',
    updated_date = NOW()
WHERE company_id IS NULL
  AND id = top_id
  AND id != 'd4a8f1b2-7c3e-4d5f-9a6b-1e2f3c4d5e6f'
  AND id != 'f6c9d3e4-5a7b-4f8c-bc2d-3e4f5a6b7c8d';


-- ============================================
-- FASE 3: COMPANIAS EXISTENTES
-- Usa CTEs para generar UUIDs unicos por compania (sin DO blocks)
-- ============================================

-- 3.1 Crear /apps para cada compania activa
WITH new_apps AS (
    SELECT uuid_generate_v4() AS id, c.id AS company_id
    FROM company c
    WHERE c.state = true
)
INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, type, created_date, updated_date)
SELECT id, company_id, 'apps', 'Aplicaciones', 'Pantalla de seleccion de aplicaciones', id, '/apps', TRUE, 'grid', 'INTERNAL', NOW(), NOW()
FROM new_apps;

-- 3.2 Crear /citas para cada compania activa
WITH new_citas AS (
    SELECT uuid_generate_v4() AS id, c.id AS company_id
    FROM company c
    WHERE c.state = true
)
INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, type, created_date, updated_date)
SELECT id, company_id, 'citas', 'Citas', 'Menu principal - Modulo de citas', id, '/citas', TRUE, 'calendar', 'INTERNAL', NOW(), NOW()
FROM new_citas;

-- 3.3 menu_permission para /apps de cada compania
INSERT INTO menu_permission (id, menu_id, permission_id, state, created_date, updated_date)
SELECT uuid_generate_v4(), m.id, 'a7d0e4f5-6b8c-4a9d-cd3e-4f5a6b7c8d9e', TRUE, NOW(), NOW()
FROM menu m
WHERE m."name" = 'apps' AND m.route = '/apps' AND m.company_id IS NOT NULL;

-- 3.4 menu_permission para /citas de cada compania
INSERT INTO menu_permission (id, menu_id, permission_id, state, created_date, updated_date)
SELECT uuid_generate_v4(), m.id, 'e5b9a2c3-8d4f-4e6a-ab7c-2f3a4d5e6f70', TRUE, NOW(), NOW()
FROM menu m
WHERE m."name" = 'citas' AND m.route = '/citas' AND m.company_id IS NOT NULL;

-- 3.5 Reasignar top_id de items raiz por compania a /citas
-- JOIN con el menu /citas de la misma compania
UPDATE menu m
SET top_id = citas.id,
    updated_date = NOW()
FROM menu citas
WHERE citas."name" = 'citas'
  AND citas.route = '/citas'
  AND citas.company_id = m.company_id
  AND m.company_id IS NOT NULL
  AND m.id = m.top_id
  AND m.id != citas.id
  AND m."name" != 'apps';


-- ============================================
-- ROLLBACK
-- ============================================

--ROLLBACK DELETE FROM rol_permission WHERE permission_id IN ('a7d0e4f5-6b8c-4a9d-cd3e-4f5a6b7c8d9e', 'e5b9a2c3-8d4f-4e6a-ab7c-2f3a4d5e6f70');
--ROLLBACK DELETE FROM menu_permission WHERE menu_id IN (SELECT id FROM menu WHERE "name" IN ('apps', 'citas') AND route IN ('/apps', '/citas'));
--ROLLBACK UPDATE menu SET top_id = id, updated_date = NOW() WHERE top_id IN (SELECT id FROM menu WHERE "name" = 'citas' AND route = '/citas') AND "name" NOT IN ('citas', 'apps');
--ROLLBACK DELETE FROM menu WHERE "name" = 'apps' AND route = '/apps';
--ROLLBACK DELETE FROM menu WHERE "name" = 'citas' AND route = '/citas';
--ROLLBACK DELETE FROM permission WHERE id IN ('a7d0e4f5-6b8c-4a9d-cd3e-4f5a6b7c8d9e', 'e5b9a2c3-8d4f-4e6a-ab7c-2f3a4d5e6f70');
```

---

## Impacto en Flujos Existentes

### Matriz de Impacto

| Flujo | Documento | Impacto | Nivel | Accion Requerida |
|-------|-----------|---------|-------|------------------|
| **Create Company** | 07-05 | La clonacion de menus template ahora incluye `/apps` y `/citas`. El `CloneMenuPermissionsForCompanyUseCase` clonara automaticamente los `menu_permission` de ambos | 🟢 Bajo | Ninguna - el algoritmo ya clona TODOS los menus `MENU_TYPE.INTERNAL` con `company_id = NULL` y sus `menu_permission` |
| **Login Interno** | 07-12 | La respuesta incluira dos nodos raiz: `/apps` (nodo hoja) y `/citas` (padre de los demas). El query en `auth_repository.menu()` filtra por `company_id` y `type = MENU_TYPE.INTERNAL`, retornara ambos nodos raiz + hijos de `/citas` | 🟢 Bajo | Ninguna - query ya cubre este caso |
| **Login Externo** | 07-12 | Ambos menus raiz (`/apps` y `/citas`) son `MENU_TYPE.INTERNAL`, no aparecen en `menu_external()` que filtra por `MENU_TYPE.EXTERNAL` | 🟢 Bajo | Ninguna |
| **Delete Company** | 07-10 | El delete eliminara `/apps` y `/citas` junto con los demas menus de la compania | 🟢 Bajo | Ninguna |
| Create User Internal | 07-01 | Sin impacto directo | ⚪ Ninguno | - |
| Create User External | 07-02 | Sin impacto directo | ⚪ Ninguno | - |
| List Users | 07-03, 07-04 | Sin impacto | ⚪ Ninguno | - |
| Delete Users | 07-08, 07-09 | Sin impacto | ⚪ Ninguno | - |
| Update User Internal | 07-11 | Sin impacto | ⚪ Ninguno | - |

### Analisis Detallado por Flujo Critico

#### 07-05: Create Company Flow

**Estado actual del codigo** (`create_company_use_case.py`, lineas 205-224):

```python
# Obtiene TODOS los menus con company_id = NULL y type = MENU_TYPE.INTERNAL
template_menus = await self.menu_list_uc.execute(
    config=config,
    params=Pagination(
        filters=[
            FilterManager(field="company_id", value=None, condition=CONDITION_TYPE.EQUALS),
            FilterManager(field="type", value="INTERNAL", condition=CONDITION_TYPE.EQUALS)
        ],
        all_data=True
    )
)
```

**Resultado post-migracion**: El query retornara ahora **N+2 menus** (los N existentes + `/apps` + `/citas`).

**`CloneMenusForCompanyUseCase`** (2 pases):
1. **Pase 1**: Generara mapping para todos (incluyendo `/apps` y `/citas`)
2. **Pase 2**: Clonara ambos como nodos raiz (`id == top_id` → `new_top_id = new_id`) y los demas con `top_id` mapeado al nuevo `/citas`

**`CloneMenuPermissionsForCompanyUseCase`**: Para ambos menus clonados (`/apps` y `/citas`), buscara las `menu_permission` del template original y creara nuevas con los `menu_id` clonados y los **mismos `permission_id`** template. Esto es exactamente lo que necesitamos.

**Conclusion**: El codigo actual **NO requiere cambios**. Ambos algoritmos manejan correctamente multiples nodos raiz.

#### 07-12: Login Flow

**Para usuarios internos** (`auth_repository.py`, metodo `menu`):

```python
.filter(MenuEntity.company_id == params.company)
.filter(MenuEntity.type == "INTERNAL")  # MENU_TYPE.INTERNAL
```

El query retorna menus por `company_id` y tipo. El `menu_permission` liga con `permission`, y `rol_permission` liga `permission` con el rol del usuario. La cadena completa:

```
usuario → user_location_rol → rol → rol_permission → permission → menu_permission → menu
```

Post-migracion: Ambos menus raiz (`/apps` y `/citas`) apareceran porque tienen toda la cadena de permisos completa (permission + menu_permission + rol_permission para ADMIN/COLLA). El frontend recibira dos nodos raiz independientes.

**Para usuarios externos** (`auth_repository.py`, metodo `menu_external`):

```python
.filter(MenuEntity.type == "EXTERNAL")  # MENU_TYPE.EXTERNAL
```

Sin cambios. Tanto `/apps` como `/citas` son `MENU_TYPE.INTERNAL`.

---

## Impacto en Codigo

### Archivos que NO Requieren Cambios

| Archivo | Razon |
|---------|-------|
| `clone_menus_for_company_use_case.py` | El algoritmo de 2 pases ya maneja jerarquias correctamente |
| `clone_menu_permissions_for_company_use_case.py` | Clona `menu_permission` basandose en mapping, funciona igual |
| `create_company_use_case.py` | Query de templates incluira automaticamente el nuevo padre |
| `auth_repository.py` | Queries de menu retornan por `company_id` y `type`, sin filtro de jerarquia |
| `menu_entity.py` | Sin cambios de esquema. Usa `UUID(as_uuid=True)` con `server_default=text('uuid_generate_v4()')` |
| `menu_repository.py` | CRUD generico, sin logica de jerarquia |
| Modelos `Menu`, `MenuSave` | Usan `UUID4` de Pydantic, compatible con UUIDs v4 generados en migracion |

### Enum Existente - MENU_TYPE

**Archivo**: `src/core/enums/menu_type.py`

```python
class MENU_TYPE(str, Enum):
    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"
```

Este enum ya existe y se usa en el codigo. La migracion es consistente con estos valores.

### Enum Existente - ROL_TYPE

**Archivo**: `src/core/enums/rol_type.py`

```python
class ROL_TYPE(str, Enum):
    ADMIN = "ADMIN"
    COLLA = "COLLA"
    USER = "USER"
```

La migracion asigna permisos a ADMIN y COLLA (no a USER, que es para usuarios externos).

### Ajuste Requerido en Frontend

El frontend que consume la respuesta de login debera manejar dos nodos raiz independientes y un nuevo nivel de jerarquia bajo `/citas`. Ver spec de frontend: `goluti-front-ia/docs/flows/16-applications-screen-flow.md`

**Antes:**
```json
{
  "menu": [
    { "id": "A", "name": "home", "topId": "A", "route": "/home" },
    { "id": "B", "name": "users", "topId": "B", "route": "/users" },
    { "id": "C", "name": "appointments", "topId": "B", "route": "/appointments" }
  ]
}
```

**Despues:**
```json
{
  "menu": [
    { "id": "APPS", "name": "apps", "topId": "APPS", "route": "/apps", "icon": "grid" },
    { "id": "CITAS", "name": "citas", "topId": "CITAS", "route": "/citas", "icon": "calendar" },
    { "id": "A", "name": "home", "topId": "CITAS", "route": "/home" },
    { "id": "B", "name": "users", "topId": "CITAS", "route": "/users" },
    { "id": "C", "name": "appointments", "topId": "B", "route": "/appointments" }
  ]
}
```

**Cambios clave:**
- Dos nodos raiz: `/apps` (nodo hoja, sin hijos) y `/citas` (padre de los items existentes)
- Items que antes eran raiz (`A`, `B`) ahora tienen `topId = CITAS`
- El frontend usa `/apps` para la pantalla de seleccion de aplicaciones y `/citas` para el dashboard con sidebar

---

## Plan de Ejecucion

### Paso 1: Crear Archivo de Migracion

Crear el archivo `migrations/changelog-v60.sql` con el contenido de la seccion [Script SQL de Migracion](#script-sql-de-migracion).

**UUIDs fijos en el script** (ya definidos, UUID v4 validos para Pydantic):
- Menu /apps template: `f6c9d3e4-5a7b-4f8c-bc2d-3e4f5a6b7c8d`
- Permission /apps template: `a7d0e4f5-6b8c-4a9d-cd3e-4f5a6b7c8d9e`
- Menu /citas template: `d4a8f1b2-7c3e-4d5f-9a6b-1e2f3c4d5e6f`
- Permission /citas template: `e5b9a2c3-8d4f-4e6a-ab7c-2f3a4d5e6f70`

### Paso 2: Ejecutar Script en Base de Datos

El usuario ejecuta el script manualmente en la base de datos:

```bash
# Ejecutar el script SQL en una sola transaccion (rollback automatico si falla)
psql --single-transaction -f migrations/changelog-v60.sql
```

### Paso 3: Validar Flujos

1. Probar **login** con usuario interno (ADMIN) → verificar que `/apps` y `/citas` aparecen como nodos raiz
2. Probar **login** con usuario interno (COLLA) → verificar que `/apps` y `/citas` aparecen como nodos raiz
3. Probar **login** con usuario externo → verificar que no se ve afectado
4. Probar **create-company** → verificar que se clonan `/apps` y `/citas` con toda su cadena de permisos
5. Verificar la jerarquia en la nueva compania creada (ambos nodos raiz presentes)

### Paso 4: Validar en Produccion

Ejecutar los queries de verificacion de la seccion [Validaciones Post-Migracion](#validaciones-post-migracion).

---

## Validaciones Post-Migracion

### Queries de Verificacion

```sql
-- 1. Verificar que existen ambos menus raiz en templates
SELECT id, name, route, top_id, type, company_id
FROM menu
WHERE name IN ('apps', 'citas') AND route IN ('/apps', '/citas') AND company_id IS NULL;
-- Resultado esperado: 2 filas (apps y citas, ambos con id == top_id)

-- 2. Verificar que existen ambos permissions template
SELECT id, name, company_id, state
FROM permission
WHERE name IN ('apps_access', 'citas_access') AND company_id IS NULL;
-- Resultado esperado: 2 filas

-- 3. Verificar menu_permission de ambos templates
SELECT mp.id, mp.menu_id, mp.permission_id, m.name as menu_name, p.name as permission_name
FROM menu_permission mp
INNER JOIN menu m ON mp.menu_id = m.id
INNER JOIN permission p ON mp.permission_id = p.id
WHERE m.name IN ('apps', 'citas') AND m.company_id IS NULL;
-- Resultado esperado: 2 filas (apps→apps_access, citas→citas_access)

-- 4. Verificar rol_permission para ADMIN y COLLA con ambos permisos
SELECT rp.id, r.code as rol_code, r.company_id, p.name as permission_name
FROM rol_permission rp
INNER JOIN rol r ON rp.rol_id = r.id
INNER JOIN permission p ON rp.permission_id = p.id
WHERE p.name IN ('apps_access', 'citas_access')
ORDER BY p.name, r.code;
-- Resultado esperado: 4 filas (ADMIN+COLLA x apps_access + citas_access)

-- 5. Verificar que todos los items raiz template apuntan al padre
-- (Solo /apps y /citas deben tener id == top_id en templates)
SELECT COUNT(*) as orphan_roots
FROM menu
WHERE company_id IS NULL
  AND id = top_id
  AND name NOT IN ('apps', 'citas');
-- Resultado esperado: 0

-- 6. Verificar que cada compania tiene ambos menus raiz
SELECT c.id as company_id, c.name as company_name,
       apps.id as apps_menu_id,
       citas.id as citas_menu_id
FROM company c
LEFT JOIN menu apps ON apps.company_id = c.id AND apps.name = 'apps' AND apps.route = '/apps'
LEFT JOIN menu citas ON citas.company_id = c.id AND citas.name = 'citas' AND citas.route = '/citas'
WHERE c.state = true;
-- Todas las companias activas deben tener apps_menu_id y citas_menu_id

-- 7. Verificar integridad de jerarquia (no deben haber top_id huerfanos)
SELECT m.id, m.name, m.top_id, m.company_id
FROM menu m
LEFT JOIN menu parent ON m.top_id = parent.id
WHERE parent.id IS NULL
  AND m.state = true;
-- Resultado esperado: 0 filas

-- 8. Verificar cadena completa para un usuario ADMIN con ambos menus raiz
-- (Debe retornar /apps y /citas en la lista de menus accesibles)
SELECT m.name, m.route, m.type, mp.permission_id, rp.rol_id, r.code
FROM menu m
INNER JOIN menu_permission mp ON mp.menu_id = m.id
INNER JOIN rol_permission rp ON rp.permission_id = mp.permission_id
INNER JOIN rol r ON rp.rol_id = r.id
WHERE m.name IN ('apps', 'citas') AND m.company_id IS NULL
ORDER BY m.name, r.code;
-- Resultado esperado: 4 filas (apps x ADMIN/COLLA, citas x ADMIN/COLLA)
```

---

## Rollback

### Procedimiento

Ejecutar los comandos `--ROLLBACK` del archivo `migrations/changelog-v60.sql` en orden (remover el prefijo `--ROLLBACK `):

El rollback (en orden inverso):

1. Elimina `rol_permission` de ambos permisos ("apps_access" y "citas_access")
2. Elimina `menu_permission` de todos los menus `/apps` y `/citas` (template y companias)
3. Restaura `top_id = id` en todos los items (template y companias) que apuntaban a un menu `/citas`
4. Elimina todos los menus `/apps` (template y por compania)
5. Elimina todos los menus `/citas` (template y por compania)
6. Elimina ambos `permission` template ("apps_access" y "citas_access")

### Riesgo del Rollback

| Riesgo | Nivel | Mitigacion |
|--------|-------|------------|
| Companias creadas post-migracion tendran `/apps` y `/citas` clonados | 🟡 Medio | El rollback busca por `name` y `route`, no por UUID, asi que los revertira |
| `rol_permission` nuevos de companias creadas post-migracion | 🟡 Medio | Se eliminan por `permission_id` |

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|------------|
| Frontend no maneja dos nodos raiz ni nuevo nivel de jerarquia | 🟡 Media | 🔴 Alto | Coordinar con frontend antes de desplegar (ver spec `16-applications-screen-flow.md`) |
| Roles ADMIN/COLLA template no existen | 🟢 Baja | 🔴 Alto | Script valida existencia antes de insertar `rol_permission` |
| UUID no v4 causa error en modelos Pydantic | 🟢 Baja | 🔴 Alto | Script usa `uuid.uuid4()` que siempre genera v4 validos |
| Timeout en migracion con muchas companias | 🟢 Baja | 🟡 Medio | Migracion itera por compania, operaciones simples |
| Inconsistencia si migracion falla a mitad | 🟢 Baja | 🔴 Alto | Ejecutar con `psql --single-transaction`; fallo = rollback completo |

---

## Referencias

| Documento | Ruta |
|-----------|------|
| **Frontend: Applications Screen Flow** | `goluti-front-ia/docs/flows/16-applications-screen-flow.md` |
| Create Company Flow | `docs/07-flows/07-05-create-company-flow.md` |
| Login Flow | `docs/07-flows/07-12-login-flow.md` |
| Delete Company Flow | `docs/07-flows/07-10-delete-company-flow.md` |
| Menu Entity | `src/infrastructure/database/entities/menu_entity.py` |
| Menu Permission Entity | `src/infrastructure/database/entities/menu_permission_entity.py` |
| Permission Entity | `src/infrastructure/database/entities/permission_entity.py` |
| Rol Entity | `src/infrastructure/database/entities/rol_entity.py` |
| Rol Permission Entity | `src/infrastructure/database/entities/rol_permission_entity.py` |
| Clone Menus Use Case | `src/domain/services/use_cases/business/auth/create_company/clone_menus_for_company_use_case.py` |
| Clone Permissions Use Case | `src/domain/services/use_cases/business/auth/create_company/clone_menu_permissions_for_company_use_case.py` |
| Auth Repository (menu queries) | `src/infrastructure/database/repositories/business/auth_repository.py` |
| MENU_TYPE Enum | `src/core/enums/menu_type.py` |
| ROL_TYPE Enum | `src/core/enums/rol_type.py` |

---

## Historial de Cambios

| Version | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0 | 2026-02-11 | Creacion inicial del spec | Equipo Goluti |
| 1.1 | 2026-02-11 | Agregar cadena completa de permisos (permission, menu_permission, rol_permission para ADMIN/COLLA). Validar UUIDs v4 para compatibilidad con modelos Pydantic. Referenciar enums MENU_TYPE y ROL_TYPE existentes. Aclarar que el script es ejecutado manualmente por el usuario | Equipo Goluti |
| 1.2 | 2026-02-11 | Migrar de formato Alembic/Python a SQL puro con formato Liquibase (changelog-v60.sql). Usar DO blocks para iteracion por compania. Usar uuid_generate_v4() nativo de PostgreSQL. Rollback en formato --ROLLBACK consistente con migraciones existentes | Equipo Goluti |
| 1.3 | 2026-02-11 | **Segunda revision**: Aclarar modelo de roles (globales con `company_id = NULL`, compartidos por todas las companias). Simplificar a 3 fases (eliminar Fase 4 redundante). Agregar `splitStatements:false` al changeset Liquibase. Cambiar `psql -f` por `psql --single-transaction -f`. Agregar guardas NOT EXISTS a INSERTs de Fase 1 y 2. Simplificar ROLLBACK (eliminar DO $ block). Corregir "Alembic" por "Liquibase" en Riesgos. Corregir espacios faltantes en queries de validacion. Corregir numeracion de pasos | Equipo Goluti |
| 1.4 | 2026-02-11 | **Agregar /apps como segundo nodo raiz**: Crear menu `/apps` (nodo hoja, pantalla de seleccion de aplicaciones) como item independiente junto a `/citas`. Ambos son nodos raiz (`id == top_id`), `INTERNAL`, con cadena completa de permisos (permission + menu_permission + rol_permission para ADMIN y COLLA). SQL de migracion reescrito con 2 permissions, 4 rol_permissions, 2 menus, 2 menu_permissions. Queries de validacion actualizados para ambos nodos. Rollback extendido. Referencia al spec de frontend (`16-applications-screen-flow.md`). UUIDs fijos: Menu /apps `f6c9d3e4-5a7b-4f8c-bc2d-3e4f5a6b7c8d`, Permission /apps `a7d0e4f5-6b8c-4a9d-cd3e-4f5a6b7c8d9e` | Equipo Goluti |
| 1.5 | 2026-02-13 | **Ajustes de implementacion**: (1) Remover `splitStatements:false` del changeset — no se usan DO blocks. (2) Remover filtro `company_id IS NULL` de queries de rol — usar solo `WHERE code = 'ADMIN' AND state = true` para mayor portabilidad entre entornos. (3) Reemplazar DO block de Fase 3 con CTEs (`WITH ... INSERT SELECT`), consistente con patron del proyecto (ningun changelog previo usa DO blocks). (4) Remover guardas NOT EXISTS, consistente con patron de v43/v46/v50. (5) Agregar double quotes a `"name"` y `"label"` en tabla menu, consistente con v43/v50. SQL del spec actualizado para coincidir con `migrations/changelog-v60.sql` | Equipo Goluti |

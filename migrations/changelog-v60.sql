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

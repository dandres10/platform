-- liquibase formatted sql
-- changeset insert-menu-servicios-hijos:1734753600000-43

-- ============================================
-- Crear submenús de Servicios (hijos del menú global)
-- top_id = c2d65172-26d5-4a5c-9c93-6fdfa9a0d41a (Servicios global)
-- ============================================

-- 1. Empresa
INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, created_date, updated_date) 
VALUES (
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d43a',
    NULL,
    'Empresa',
    'menu.services_company',
    'menu.services_company_description',
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d41a',
    '/services/company',
    true,
    'building',
    now(),
    now()
);

-- 2. Sede
INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, created_date, updated_date) 
VALUES (
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d43b',
    NULL,
    'Sede',
    'menu.services_location',
    'menu.services_location_description',
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d41a',
    '/services/location',
    true,
    'map-pin',
    now(),
    now()
);

-- 3. Colaborador
INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, created_date, updated_date) 
VALUES (
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d43c',
    NULL,
    'Colaborador',
    'menu.services_collaborator',
    'menu.services_collaborator_description',
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d41a',
    '/services/collaborator',
    true,
    'user',
    now(),
    now()
);

-- ============================================
-- Crear submenús de Servicios para compañía específica
-- company_id = 1f9a2dd5-2cf6-4350-b3d1-10dc4e8ba730
-- top_id = c2d65172-26d5-4a5c-9c93-6fdfa9a0d41b (Servicios de la compañía)
-- ============================================

-- 1. Empresa (compañía)
INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, created_date, updated_date) 
VALUES (
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d45a',
    '1f9a2dd5-2cf6-4350-b3d1-10dc4e8ba730',
    'Empresa',
    'menu.services_company',
    'menu.services_company_description',
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d41b',
    '/services/company',
    true,
    'building',
    now(),
    now()
);

-- 2. Sede (compañía)
INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, created_date, updated_date) 
VALUES (
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d45b',
    '1f9a2dd5-2cf6-4350-b3d1-10dc4e8ba730',
    'Sede',
    'menu.services_location',
    'menu.services_location_description',
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d41b',
    '/services/location',
    true,
    'map-pin',
    now(),
    now()
);

-- 3. Colaborador (compañía)
INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, created_date, updated_date) 
VALUES (
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d45c',
    '1f9a2dd5-2cf6-4350-b3d1-10dc4e8ba730',
    'Colaborador',
    'menu.services_collaborator',
    'menu.services_collaborator_description',
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d41b',
    '/services/collaborator',
    true,
    'user',
    now(),
    now()
);

-- ============================================
-- Crear permisos para los submenús de Servicios
-- ============================================

-- Permiso SERVICES_COMPANY
INSERT INTO permission (id, company_id, name, description, state, created_date, updated_date)
VALUES (
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d44a',
    NULL,
    'SERVICES_COMPANY',
    'Permite al usuario acceder al menú de servicios de empresa',
    TRUE,
    NOW(),
    NOW()
);

-- Permiso SERVICES_LOCATION
INSERT INTO permission (id, company_id, name, description, state, created_date, updated_date)
VALUES (
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d44b',
    NULL,
    'SERVICES_LOCATION',
    'Permite al usuario acceder al menú de servicios de sede',
    TRUE,
    NOW(),
    NOW()
);

-- Permiso SERVICES_COLLABORATOR
INSERT INTO permission (id, company_id, name, description, state, created_date, updated_date)
VALUES (
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d44c',
    NULL,
    'SERVICES_COLLABORATOR',
    'Permite al usuario acceder al menú de servicios de colaborador',
    TRUE,
    NOW(),
    NOW()
);

-- ============================================
-- Crear relaciones menu_permission
-- ============================================

-- Relación Empresa - SERVICES_COMPANY
INSERT INTO menu_permission (id, menu_id, permission_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d43a',
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d44a',
    TRUE,
    NOW(),
    NOW()
);

-- Relación Sede - SERVICES_LOCATION
INSERT INTO menu_permission (id, menu_id, permission_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d43b',
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d44b',
    TRUE,
    NOW(),
    NOW()
);

-- Relación Colaborador - SERVICES_COLLABORATOR
INSERT INTO menu_permission (id, menu_id, permission_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d43c',
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d44c',
    TRUE,
    NOW(),
    NOW()
);

-- ============================================
-- Relaciones menu_permission para compañía
-- ============================================

-- Relación Empresa (compañía) - SERVICES_COMPANY
INSERT INTO menu_permission (id, menu_id, permission_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d45a',
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d44a',
    TRUE,
    NOW(),
    NOW()
);

-- Relación Sede (compañía) - SERVICES_LOCATION
INSERT INTO menu_permission (id, menu_id, permission_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d45b',
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d44b',
    TRUE,
    NOW(),
    NOW()
);

-- Relación Colaborador (compañía) - SERVICES_COLLABORATOR
INSERT INTO menu_permission (id, menu_id, permission_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d45c',
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d44c',
    TRUE,
    NOW(),
    NOW()
);

-- ============================================
-- Asignar permisos al rol
-- rol_id = b2f212eb-18c2-4260-9223-897685086904
-- ============================================

-- Rol - SERVICES_COMPANY
INSERT INTO rol_permission (id, rol_id, permission_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),
    'b2f212eb-18c2-4260-9223-897685086904',
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d44a',
    TRUE,
    NOW(),
    NOW()
);

-- Rol - SERVICES_LOCATION
INSERT INTO rol_permission (id, rol_id, permission_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),
    'b2f212eb-18c2-4260-9223-897685086904',
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d44b',
    TRUE,
    NOW(),
    NOW()
);

-- Rol - SERVICES_COLLABORATOR
INSERT INTO rol_permission (id, rol_id, permission_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),
    'b2f212eb-18c2-4260-9223-897685086904',
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d44c',
    TRUE,
    NOW(),
    NOW()
);

--ROLLBACK DELETE FROM rol_permission WHERE rol_id = 'b2f212eb-18c2-4260-9223-897685086904' AND permission_id IN ('c2d65172-26d5-4a5c-9c93-6fdfa9a0d44a', 'c2d65172-26d5-4a5c-9c93-6fdfa9a0d44b', 'c2d65172-26d5-4a5c-9c93-6fdfa9a0d44c');
--ROLLBACK DELETE FROM menu_permission WHERE menu_id IN ('c2d65172-26d5-4a5c-9c93-6fdfa9a0d43a', 'c2d65172-26d5-4a5c-9c93-6fdfa9a0d43b', 'c2d65172-26d5-4a5c-9c93-6fdfa9a0d43c', 'c2d65172-26d5-4a5c-9c93-6fdfa9a0d45a', 'c2d65172-26d5-4a5c-9c93-6fdfa9a0d45b', 'c2d65172-26d5-4a5c-9c93-6fdfa9a0d45c');
--ROLLBACK DELETE FROM permission WHERE id IN ('c2d65172-26d5-4a5c-9c93-6fdfa9a0d44a', 'c2d65172-26d5-4a5c-9c93-6fdfa9a0d44b', 'c2d65172-26d5-4a5c-9c93-6fdfa9a0d44c');
--ROLLBACK DELETE FROM menu WHERE id IN ('c2d65172-26d5-4a5c-9c93-6fdfa9a0d43a', 'c2d65172-26d5-4a5c-9c93-6fdfa9a0d43b', 'c2d65172-26d5-4a5c-9c93-6fdfa9a0d43c', 'c2d65172-26d5-4a5c-9c93-6fdfa9a0d45a', 'c2d65172-26d5-4a5c-9c93-6fdfa9a0d45b', 'c2d65172-26d5-4a5c-9c93-6fdfa9a0d45c');


-- liquibase formatted sql
-- changeset insert-menu-servicios:1734746400000-41

-- ============================================
-- Crear menú Servicios (global y para compañía)
-- ============================================

-- 1. Menú Servicios global (company_id = NULL)
INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, created_date, updated_date) 
VALUES (
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d41a',
    NULL,
    'Servicios',
    'menu.services',
    'menu.services_description',
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d41a',
    '/services',
    true,
    'briefcase',
    now(),
    now()
);

-- 2. Menú Servicios para compañía específica
INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, created_date, updated_date) 
VALUES (
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d41b',
    '1f9a2dd5-2cf6-4350-b3d1-10dc4e8ba730',
    'Servicios',
    'menu.services',
    'menu.services_description',
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d41b',
    '/services',
    true,
    'briefcase',
    now(),
    now()
);

-- ============================================
-- Crear permiso SERVICES
-- ============================================

INSERT INTO permission (
    id, 
    company_id, 
    name, 
    description, 
    state, 
    created_date, 
    updated_date
)
VALUES (
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d41c',
    NULL, 
    'SERVICES',
    'Permite al usuario acceder al menú de servicios', 
    TRUE,
    NOW(),
    NOW()
);

-- ============================================
-- Crear relaciones menu_permission
-- ============================================

-- Relación para menú global
INSERT INTO menu_permission (
    id, 
    menu_id, 
    permission_id, 
    state, 
    created_date, 
    updated_date
)
VALUES (
    uuid_generate_v4(),
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d41a',
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d41c',
    TRUE, 
    NOW(), 
    NOW()
);

-- Relación para menú de compañía
INSERT INTO menu_permission (
    id, 
    menu_id, 
    permission_id, 
    state, 
    created_date, 
    updated_date
)
VALUES (
    uuid_generate_v4(),
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d41b',
    'c2d65172-26d5-4a5c-9c93-6fdfa9a0d41c',
    TRUE, 
    NOW(), 
    NOW()
);

--ROLLBACK DELETE FROM menu_permission WHERE menu_id IN ('c2d65172-26d5-4a5c-9c93-6fdfa9a0d41a', 'c2d65172-26d5-4a5c-9c93-6fdfa9a0d41b');
--ROLLBACK DELETE FROM permission WHERE id = 'c2d65172-26d5-4a5c-9c93-6fdfa9a0d41c';
--ROLLBACK DELETE FROM menu WHERE id IN ('c2d65172-26d5-4a5c-9c93-6fdfa9a0d41a', 'c2d65172-26d5-4a5c-9c93-6fdfa9a0d41b');


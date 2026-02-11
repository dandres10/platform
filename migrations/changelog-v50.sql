-- liquibase formatted sql
-- changeset add-external-menu-inicio:1736963400000-50

-- ============================================
-- MIGRACIÓN: Agregar menú "Inicio" para usuarios externos
-- 
-- Este menú es global (company_id = NULL) y exclusivo para
-- usuarios externos (type = 'EXTERNAL').
--
-- Tablas afectadas:
-- 1. menu - El item del menú
-- 2. permission - El permiso asociado
-- 3. menu_permission - Relación menú-permiso
-- 4. rol_permission - Asignación del permiso al rol USER
-- ============================================

-- ============================================
-- 1. Crear menú "Inicio" para usuarios externos
-- ============================================

INSERT INTO menu (
    id, 
    company_id, 
    "name", 
    "label", 
    description, 
    top_id, 
    route, 
    state, 
    icon,
    type,
    created_date, 
    updated_date
) 
VALUES (
    'b1d65172-26d5-4a5c-9c93-6fdfa9a0d50a',
    NULL,                                        -- Global, sin compañía
    'Inicio',
    'menu.external_home',
    'menu.external_home_description',
    'b1d65172-26d5-4a5c-9c93-6fdfa9a0d50a',     -- Es su propio padre (menú raíz)
    '/user/home',
    TRUE,
    'home',
    'EXTERNAL',                                  -- Tipo EXTERNAL para usuarios externos
    NOW(),
    NOW()
);

-- ============================================
-- 2. Crear permiso para "Inicio" externo
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
    'b1d65172-26d5-4a5c-9c93-6fdfa9a0d50b',
    NULL,                                        -- Global, sin compañía
    'EXTERNAL_HOME',
    'Permite al usuario externo acceder al menú de inicio',
    TRUE,
    NOW(),
    NOW()
);

-- ============================================
-- 3. Crear relación menu_permission
-- Asocia el menú con su permiso
-- ============================================

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
    'b1d65172-26d5-4a5c-9c93-6fdfa9a0d50a',     -- menu_id: Inicio
    'b1d65172-26d5-4a5c-9c93-6fdfa9a0d50b',     -- permission_id: EXTERNAL_HOME
    TRUE,
    NOW(),
    NOW()
);

-- ============================================
-- 4. Asignar permiso EXTERNAL_HOME al rol USER
-- rol_id = 1214ffde-997c-4482-b7fe-2524c828a188
-- ============================================

INSERT INTO rol_permission (
    id, 
    rol_id, 
    permission_id, 
    state, 
    created_date, 
    updated_date
)
VALUES (
    uuid_generate_v4(),
    '1214ffde-997c-4482-b7fe-2524c828a188',     -- rol_id: USER (usuarios externos)
    'b1d65172-26d5-4a5c-9c93-6fdfa9a0d50b',     -- permission_id: EXTERNAL_HOME
    TRUE,
    NOW(),
    NOW()
);

-- ============================================
-- ROLLBACK
-- ============================================

--ROLLBACK DELETE FROM rol_permission WHERE permission_id = 'b1d65172-26d5-4a5c-9c93-6fdfa9a0d50b';
--ROLLBACK DELETE FROM menu_permission WHERE menu_id = 'b1d65172-26d5-4a5c-9c93-6fdfa9a0d50a';
--ROLLBACK DELETE FROM permission WHERE id = 'b1d65172-26d5-4a5c-9c93-6fdfa9a0d50b';
--ROLLBACK DELETE FROM menu WHERE id = 'b1d65172-26d5-4a5c-9c93-6fdfa9a0d50a';

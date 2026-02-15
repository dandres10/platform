-- liquibase formatted sql
-- changeset delete-user-redundant-menus:1739404800000-61

-- ============================================
-- MIGRACION: Eliminar menus redundantes del rol USER
--
-- Se eliminan 2 items:
-- 1. "Home"      (route: /home)             - 7e16d1e1-ca05-416f-8514-c7f24e9cdb4f
-- 2. "Mis Citas" (route: /my-appointments)  - a0b65172-26d5-4a5c-9c93-6fdfa9a0d46a
--
-- El USER solo conserva:
-- - "Inicio" (/user/home) - Pagina principal del usuario
--
-- Tablas afectadas:
-- 1. rol_permission (DELETE cascada)
-- 2. menu_permission (DELETE cascada)
-- 3. menu (DELETE x2)
-- ============================================


-- ============================================
-- FASE 1: LIMPIAR PERMISOS ASOCIADOS
-- ============================================

-- 1.1 Eliminar rol_permission asociados a ambos menus via menu_permission
DELETE FROM rol_permission
WHERE permission_id IN (
    SELECT mp.permission_id
    FROM menu_permission mp
    WHERE mp.menu_id IN (
        '7e16d1e1-ca05-416f-8514-c7f24e9cdb4f',
        'a0b65172-26d5-4a5c-9c93-6fdfa9a0d46a'
    )
);

-- 1.2 Eliminar menu_permission de ambos menus
DELETE FROM menu_permission
WHERE menu_id IN (
    '7e16d1e1-ca05-416f-8514-c7f24e9cdb4f',
    'a0b65172-26d5-4a5c-9c93-6fdfa9a0d46a'
);


-- ============================================
-- FASE 2: ELIMINAR MENUS
-- ============================================

-- 2.1 Eliminar "Home" y "Mis Citas"
DELETE FROM menu
WHERE id IN (
    '7e16d1e1-ca05-416f-8514-c7f24e9cdb4f',
    'a0b65172-26d5-4a5c-9c93-6fdfa9a0d46a'
);


-- ============================================
-- ROLLBACK
-- ============================================

--ROLLBACK INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, type, created_date, updated_date) VALUES ('7e16d1e1-ca05-416f-8514-c7f24e9cdb4f', NULL, 'Home', 'menu.home', 'menu.home_description', 'd4a8f1b2-7c3e-4d5f-9a6b-1e2f3c4d5e6f', '/home', TRUE, 'home', 'INTERNAL', NOW(), NOW());
--ROLLBACK INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, type, created_date, updated_date) VALUES ('a0b65172-26d5-4a5c-9c93-6fdfa9a0d46a', NULL, 'Mis Citas', 'menu.my_appointments', 'menu.my_appointments_description', 'd4a8f1b2-7c3e-4d5f-9a6b-1e2f3c4d5e6f', '/my-appointments', TRUE, 'calendar', 'INTERNAL', NOW(), NOW());

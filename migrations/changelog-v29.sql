-- liquibase formatted sql
-- changeset insert-global-menus:1731445800000-29


-- Script para duplicar registros de menu con company_id NULL (menús globales)
-- Mantiene las relaciones jerárquicas entre registros padre (cabeza) e hijos

-- ============================================
-- REGISTROS CABEZA (id == top_id)
-- ============================================

-- 1. Citas (Cabeza) - Original: a0b65172-26d5-4a5c-9c93-6fdfa9a0d39e
-- Nuevo UUID: a0b65172-26d5-4a5c-9c93-6fdfa9a0d39f
INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, created_date, updated_date) 
VALUES (
    'a0b65172-26d5-4a5c-9c93-6fdfa9a0d39f',
    NULL,
    'Citas',
    'Organiza todas tus citas',
    'Puedes realizar todo con respecto a citas',
    'a0b65172-26d5-4a5c-9c93-6fdfa9a0d39f', -- Mismo ID porque es cabeza
    '/appointment/home',
    true,
    'home-icon',
    now(),
    now()
);

-- 2. Home (Cabeza) - Original: 7e16d1e1-ca05-416f-8514-c7f24e9cdb3e
-- Nuevo UUID: 7e16d1e1-ca05-416f-8514-c7f24e9cdb3f
INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, created_date, updated_date) 
VALUES (
    '7e16d1e1-ca05-416f-8514-c7f24e9cdb3f',
    NULL,
    'Home',
    'Encuentra todo acá',
    'Home for the application',
    '7e16d1e1-ca05-416f-8514-c7f24e9cdb3f', -- Mismo ID porque es cabeza
    '/platform/home',
    true,
    'home-icon',
    now(),
    now()
);

-- 3. Home (Cabeza) - Original: a0b65172-26d5-4a5c-9c93-6fdfa9a0d38e
-- Nuevo UUID: a0b65172-26d5-4a5c-9c93-6fdfa9a0d38f
INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, created_date, updated_date) 
VALUES (
    'a0b65172-26d5-4a5c-9c93-6fdfa9a0d38f',
    NULL,
    'Home',
    'Encuentra todo acá',
    'Home for the application',
    'a0b65172-26d5-4a5c-9c93-6fdfa9a0d38f', -- Mismo ID porque es cabeza
    '/platform/home',
    true,
    'home-icon',
    now(),
    now()
);

-- ============================================
-- REGISTROS HIJOS (id != top_id)
-- ============================================

-- 4. Crear (Hijo de Citas) - Original: a0b65172-26d5-4a5c-9c93-6fdfa9a0d37e
-- Nuevo UUID: a0b65172-26d5-4a5c-9c93-6fdfa9a0d37f
-- top_id debe apuntar al nuevo UUID de la cabeza "Citas": a0b65172-26d5-4a5c-9c93-6fdfa9a0d39f
INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, created_date, updated_date) 
VALUES (
    'a0b65172-26d5-4a5c-9c93-6fdfa9a0d37f',
    NULL,
    'Crear',
    'Crea citas',
    'crea citas',
    'a0b65172-26d5-4a5c-9c93-6fdfa9a0d39f', -- Apunta al nuevo UUID de la cabeza "Citas"
    '/appointment/create',
    true,
    'home-icon',
    now(),
    now()
);


--ROLLBACK DELETE FROM menu WHERE company_id IS NULL AND id IN ('a0b65172-26d5-4a5c-9c93-6fdfa9a0d39f', '7e16d1e1-ca05-416f-8514-c7f24e9cdb3f', 'a0b65172-26d5-4a5c-9c93-6fdfa9a0d38f', 'a0b65172-26d5-4a5c-9c93-6fdfa9a0d37f');


-- liquibase formatted sql
-- changeset add-chat-history-menu:1740240000000-63

-- ============================================
-- MIGRACION: Agregar menu "Historial de Chats"
--
-- Crea un item de menu para todos los roles (ADMIN, COLLA, USER)
-- tanto para tipo INTERNAL (bajo Citas) como EXTERNAL.
--
-- UUIDs fijos para templates:
-- Menu INTERNAL:     c8f1a2b3-4d5e-6f7a-8b9c-0d1e2f3a4b5c
-- Menu EXTERNAL:     c8f1a2b3-4d5e-6f7a-8b9c-0d1e2f3a4b5d
-- Permission:        c8f1a2b3-4d5e-6f7a-8b9c-0d1e2f3a4b5e
--
-- Tablas afectadas:
-- 1. permission (INSERT x1)
-- 2. rol_permission (INSERT x3: ADMIN, COLLA, USER)
-- 3. menu (INSERT x2 templates + INSERT x2 por compania)
-- 4. menu_permission (INSERT x2 templates + INSERT x2 por compania)
-- ============================================

--RUN

-- ============================================
-- FASE 1: PERMISSION Y ROLES TEMPLATE
-- ============================================

-- 1.1 Crear permission chat_history_access
INSERT INTO permission (id, company_id, name, description, state, created_date, updated_date)
VALUES (
    'c8f1a2b3-4d5e-6f7a-8b9c-0d1e2f3a4b5e',
    NULL,
    'chat_history_access',
    'Permiso de acceso al historial de chats',
    TRUE,
    NOW(),
    NOW()
);

-- 1.2 rol_permission: ADMIN + chat_history_access
INSERT INTO rol_permission (id, rol_id, permission_id, state, created_date, updated_date)
SELECT uuid_generate_v4(), r.id, 'c8f1a2b3-4d5e-6f7a-8b9c-0d1e2f3a4b5e', TRUE, NOW(), NOW()
FROM rol r WHERE r.code = 'ADMIN' AND r.state = true;

-- 1.3 rol_permission: COLLA + chat_history_access
INSERT INTO rol_permission (id, rol_id, permission_id, state, created_date, updated_date)
SELECT uuid_generate_v4(), r.id, 'c8f1a2b3-4d5e-6f7a-8b9c-0d1e2f3a4b5e', TRUE, NOW(), NOW()
FROM rol r WHERE r.code = 'COLLA' AND r.state = true;

-- 1.4 rol_permission: USER + chat_history_access
INSERT INTO rol_permission (id, rol_id, permission_id, state, created_date, updated_date)
SELECT uuid_generate_v4(), r.id, 'c8f1a2b3-4d5e-6f7a-8b9c-0d1e2f3a4b5e', TRUE, NOW(), NOW()
FROM rol r WHERE r.code = 'USER' AND r.state = true;


-- ============================================
-- FASE 2: MENUS TEMPLATE
-- ============================================

-- 2.1 Menu INTERNAL (hijo de Citas: d4a8f1b2-7c3e-4d5f-9a6b-1e2f3c4d5e6f)
INSERT INTO menu (id, company_id, "name", label, description, top_id, route, state, icon, type, created_date, updated_date)
VALUES (
    'c8f1a2b3-4d5e-6f7a-8b9c-0d1e2f3a4b5c',
    NULL,
    'Chat History',
    'menu.chat_history',
    'Historial de conversaciones con el asistente',
    'd4a8f1b2-7c3e-4d5f-9a6b-1e2f3c4d5e6f',
    '/system/chat-history',
    TRUE,
    'message-square',
    'INTERNAL',
    NOW(),
    NOW()
);

-- 2.2 Menu EXTERNAL (hijo de Citas: d4a8f1b2-7c3e-4d5f-9a6b-1e2f3c4d5e6f)
INSERT INTO menu (id, company_id, "name", label, description, top_id, route, state, icon, type, created_date, updated_date)
VALUES (
    'c8f1a2b3-4d5e-6f7a-8b9c-0d1e2f3a4b5d',
    NULL,
    'Chat History',
    'menu.chat_history',
    'Historial de conversaciones con el asistente',
    'd4a8f1b2-7c3e-4d5f-9a6b-1e2f3c4d5e6f',
    '/system/chat-history',
    TRUE,
    'message-square',
    'EXTERNAL',
    NOW(),
    NOW()
);

-- 2.3 menu_permission para INTERNAL template
INSERT INTO menu_permission (id, menu_id, permission_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),
    'c8f1a2b3-4d5e-6f7a-8b9c-0d1e2f3a4b5c',
    'c8f1a2b3-4d5e-6f7a-8b9c-0d1e2f3a4b5e',
    TRUE,
    NOW(),
    NOW()
);

-- 2.4 menu_permission para EXTERNAL template
INSERT INTO menu_permission (id, menu_id, permission_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),
    'c8f1a2b3-4d5e-6f7a-8b9c-0d1e2f3a4b5d',
    'c8f1a2b3-4d5e-6f7a-8b9c-0d1e2f3a4b5e',
    TRUE,
    NOW(),
    NOW()
);


-- ============================================
-- FASE 3: COMPANIAS EXISTENTES
-- ============================================

-- 3.1 Crear menu INTERNAL para cada compania activa
WITH new_internal AS (
    SELECT uuid_generate_v4() AS id, c.id AS company_id
    FROM company c WHERE c.state = true
)
INSERT INTO menu (id, company_id, "name", label, description, top_id, route, state, icon, type, created_date, updated_date)
SELECT
    ni.id,
    ni.company_id,
    'Chat History',
    'menu.chat_history',
    'Historial de conversaciones con el asistente',
    citas.id,
    '/system/chat-history',
    TRUE,
    'message-square',
    'INTERNAL',
    NOW(),
    NOW()
FROM new_internal ni
JOIN menu citas ON citas."name" = 'citas' AND citas.route = '/citas' AND citas.company_id = ni.company_id;

-- 3.2 menu_permission para INTERNAL de cada compania
INSERT INTO menu_permission (id, menu_id, permission_id, state, created_date, updated_date)
SELECT uuid_generate_v4(), m.id, 'c8f1a2b3-4d5e-6f7a-8b9c-0d1e2f3a4b5e', TRUE, NOW(), NOW()
FROM menu m
WHERE m."name" = 'Chat History'
  AND m.route = '/system/chat-history'
  AND m.type = 'INTERNAL'
  AND m.company_id IS NOT NULL;

-- 3.3 Crear menu EXTERNAL para cada compania activa
WITH new_external AS (
    SELECT uuid_generate_v4() AS id, c.id AS company_id
    FROM company c WHERE c.state = true
)
INSERT INTO menu (id, company_id, "name", label, description, top_id, route, state, icon, type, created_date, updated_date)
SELECT
    ne.id,
    ne.company_id,
    'Chat History',
    'menu.chat_history',
    'Historial de conversaciones con el asistente',
    citas.id,
    '/system/chat-history',
    TRUE,
    'message-square',
    'EXTERNAL',
    NOW(),
    NOW()
FROM new_external ne
JOIN menu citas ON citas."name" = 'citas' AND citas.route = '/citas' AND citas.company_id = ne.company_id;

-- 3.4 menu_permission para EXTERNAL de cada compania
INSERT INTO menu_permission (id, menu_id, permission_id, state, created_date, updated_date)
SELECT uuid_generate_v4(), m.id, 'c8f1a2b3-4d5e-6f7a-8b9c-0d1e2f3a4b5e', TRUE, NOW(), NOW()
FROM menu m
WHERE m."name" = 'Chat History'
  AND m.route = '/system/chat-history'
  AND m.type = 'EXTERNAL'
  AND m.company_id IS NOT NULL;

--FIN RUN

--ROLLBACK
DELETE FROM menu_permission WHERE permission_id = 'c8f1a2b3-4d5e-6f7a-8b9c-0d1e2f3a4b5e';
DELETE FROM rol_permission WHERE permission_id = 'c8f1a2b3-4d5e-6f7a-8b9c-0d1e2f3a4b5e';
DELETE FROM menu WHERE "name" = 'Chat History' AND route = '/system/chat-history';
DELETE FROM permission WHERE id = 'c8f1a2b3-4d5e-6f7a-8b9c-0d1e2f3a4b5e';
--FIN ROLLBACK

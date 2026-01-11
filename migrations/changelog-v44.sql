-- liquibase formatted sql
-- changeset insert-menu-agenda:1734760000000-44

-- ============================================
-- MENÚ AGENDA - Global (company_id = NULL)
-- ============================================

-- Menú principal Agenda (global)
INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, created_date, updated_date) 
VALUES (
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d44a',
    NULL,
    'Agenda',
    'menu.agenda',
    'menu.agenda_description',
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d44a',
    '/agenda',
    true,
    'calendar',
    now(),
    now()
);

-- Submenú Horarios (global)
INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, created_date, updated_date) 
VALUES (
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d44b',
    NULL,
    'Horarios',
    'menu.agenda_schedules',
    'menu.agenda_schedules_description',
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d44a',
    '/agenda/schedules',
    true,
    'clock',
    now(),
    now()
);

-- Submenú Ausencias (global)
INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, created_date, updated_date) 
VALUES (
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d44c',
    NULL,
    'Ausencias',
    'menu.agenda_absences',
    'menu.agenda_absences_description',
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d44a',
    '/agenda/absences',
    true,
    'user-x',
    now(),
    now()
);

-- ============================================
-- MENÚ AGENDA - Compañía específica
-- company_id = 1f9a2dd5-2cf6-4350-b3d1-10dc4e8ba730
-- ============================================

-- Menú principal Agenda (compañía)
INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, created_date, updated_date) 
VALUES (
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d45a',
    '1f9a2dd5-2cf6-4350-b3d1-10dc4e8ba730',
    'Agenda',
    'menu.agenda',
    'menu.agenda_description',
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d45a',
    '/agenda',
    true,
    'calendar',
    now(),
    now()
);

-- Submenú Horarios (compañía)
INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, created_date, updated_date) 
VALUES (
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d45b',
    '1f9a2dd5-2cf6-4350-b3d1-10dc4e8ba730',
    'Horarios',
    'menu.agenda_schedules',
    'menu.agenda_schedules_description',
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d45a',
    '/agenda/schedules',
    true,
    'clock',
    now(),
    now()
);

-- Submenú Ausencias (compañía)
INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, created_date, updated_date) 
VALUES (
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d45c',
    '1f9a2dd5-2cf6-4350-b3d1-10dc4e8ba730',
    'Ausencias',
    'menu.agenda_absences',
    'menu.agenda_absences_description',
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d45a',
    '/agenda/absences',
    true,
    'user-x',
    now(),
    now()
);

-- ============================================
-- PERMISOS
-- ============================================

-- Permiso AGENDA
INSERT INTO permission (id, company_id, name, description, state, created_date, updated_date)
VALUES (
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d46a',
    NULL,
    'AGENDA',
    'Permite al usuario acceder al menú de agenda',
    TRUE,
    NOW(),
    NOW()
);

-- Permiso AGENDA_SCHEDULES
INSERT INTO permission (id, company_id, name, description, state, created_date, updated_date)
VALUES (
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d46b',
    NULL,
    'AGENDA_SCHEDULES',
    'Permite al usuario acceder a la gestión de horarios',
    TRUE,
    NOW(),
    NOW()
);

-- Permiso AGENDA_ABSENCES
INSERT INTO permission (id, company_id, name, description, state, created_date, updated_date)
VALUES (
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d46c',
    NULL,
    'AGENDA_ABSENCES',
    'Permite al usuario acceder a la gestión de ausencias',
    TRUE,
    NOW(),
    NOW()
);

-- ============================================
-- MENU_PERMISSION - Global
-- ============================================

-- Agenda global - AGENDA
INSERT INTO menu_permission (id, menu_id, permission_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d44a',
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d46a',
    TRUE,
    NOW(),
    NOW()
);

-- Horarios global - AGENDA_SCHEDULES
INSERT INTO menu_permission (id, menu_id, permission_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d44b',
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d46b',
    TRUE,
    NOW(),
    NOW()
);

-- Ausencias global - AGENDA_ABSENCES
INSERT INTO menu_permission (id, menu_id, permission_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d44c',
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d46c',
    TRUE,
    NOW(),
    NOW()
);

-- ============================================
-- MENU_PERMISSION - Compañía
-- ============================================

-- Agenda compañía - AGENDA
INSERT INTO menu_permission (id, menu_id, permission_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d45a',
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d46a',
    TRUE,
    NOW(),
    NOW()
);

-- Horarios compañía - AGENDA_SCHEDULES
INSERT INTO menu_permission (id, menu_id, permission_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d45b',
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d46b',
    TRUE,
    NOW(),
    NOW()
);

-- Ausencias compañía - AGENDA_ABSENCES
INSERT INTO menu_permission (id, menu_id, permission_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d45c',
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d46c',
    TRUE,
    NOW(),
    NOW()
);

-- ============================================
-- ROL_PERMISSION
-- rol_id = b2f212eb-18c2-4260-9223-897685086904
-- ============================================

-- Rol - AGENDA
INSERT INTO rol_permission (id, rol_id, permission_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),
    'b2f212eb-18c2-4260-9223-897685086904',
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d46a',
    TRUE,
    NOW(),
    NOW()
);

-- Rol - AGENDA_SCHEDULES
INSERT INTO rol_permission (id, rol_id, permission_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),
    'b2f212eb-18c2-4260-9223-897685086904',
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d46b',
    TRUE,
    NOW(),
    NOW()
);

-- Rol - AGENDA_ABSENCES
INSERT INTO rol_permission (id, rol_id, permission_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),
    'b2f212eb-18c2-4260-9223-897685086904',
    'd3e65172-26d5-4a5c-9c93-6fdfa9a0d46c',
    TRUE,
    NOW(),
    NOW()
);

--ROLLBACK DELETE FROM rol_permission WHERE rol_id = 'b2f212eb-18c2-4260-9223-897685086904' AND permission_id IN ('d3e65172-26d5-4a5c-9c93-6fdfa9a0d46a', 'd3e65172-26d5-4a5c-9c93-6fdfa9a0d46b', 'd3e65172-26d5-4a5c-9c93-6fdfa9a0d46c');
--ROLLBACK DELETE FROM menu_permission WHERE menu_id IN ('d3e65172-26d5-4a5c-9c93-6fdfa9a0d44a', 'd3e65172-26d5-4a5c-9c93-6fdfa9a0d44b', 'd3e65172-26d5-4a5c-9c93-6fdfa9a0d44c', 'd3e65172-26d5-4a5c-9c93-6fdfa9a0d45a', 'd3e65172-26d5-4a5c-9c93-6fdfa9a0d45b', 'd3e65172-26d5-4a5c-9c93-6fdfa9a0d45c');
--ROLLBACK DELETE FROM permission WHERE id IN ('d3e65172-26d5-4a5c-9c93-6fdfa9a0d46a', 'd3e65172-26d5-4a5c-9c93-6fdfa9a0d46b', 'd3e65172-26d5-4a5c-9c93-6fdfa9a0d46c');
--ROLLBACK DELETE FROM menu WHERE id IN ('d3e65172-26d5-4a5c-9c93-6fdfa9a0d44a', 'd3e65172-26d5-4a5c-9c93-6fdfa9a0d44b', 'd3e65172-26d5-4a5c-9c93-6fdfa9a0d44c', 'd3e65172-26d5-4a5c-9c93-6fdfa9a0d45a', 'd3e65172-26d5-4a5c-9c93-6fdfa9a0d45b', 'd3e65172-26d5-4a5c-9c93-6fdfa9a0d45c');

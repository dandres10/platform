-- liquibase formatted sql
-- changeset update-menu-citas-and-create-mis-citas:1736617800000-46

-- ============================================
-- 1. Actualizar menú "Citas" a "Gestión de Citas"
-- ID: a0b65172-26d5-4a5c-9c93-6fdfa9a0d39f
-- ============================================

UPDATE menu 
SET name = 'Gestión de Citas',
    label = 'menu.appointments_management',
    description = 'menu.appointments_management_description',
    route = '/appointments-management',
    icon = 'clock',
    updated_date = NOW()
WHERE id = 'a0b65172-26d5-4a5c-9c93-6fdfa9a0d39f';

-- ============================================
-- 2. Crear nuevo menú "Mis Citas" (Global)
-- ============================================

INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, created_date, updated_date) 
VALUES (
    'a0b65172-26d5-4a5c-9c93-6fdfa9a0d46a',
    NULL,
    'Mis Citas',
    'menu.my_appointments',
    'menu.my_appointments_description',
    'a0b65172-26d5-4a5c-9c93-6fdfa9a0d46a',
    '/my-appointments',
    true,
    'calendar',
    NOW(),
    NOW()
);

-- ============================================
-- 3. Crear permiso para "Mis Citas"
-- ============================================

INSERT INTO permission (id, company_id, name, description, state, created_date, updated_date)
VALUES (
    'a0b65172-26d5-4a5c-9c93-6fdfa9a0d46b',
    NULL,
    'MY_APPOINTMENTS',
    'Permite al usuario acceder al menú de mis citas',
    TRUE,
    NOW(),
    NOW()
);

-- ============================================
-- 4. Crear relación menu_permission para "Mis Citas"
-- ============================================

INSERT INTO menu_permission (id, menu_id, permission_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),
    'a0b65172-26d5-4a5c-9c93-6fdfa9a0d46a',
    'a0b65172-26d5-4a5c-9c93-6fdfa9a0d46b',
    TRUE,
    NOW(),
    NOW()
);

-- ============================================
-- 5. Asignar permiso MY_APPOINTMENTS al rol de usuario
-- rol_id = 1214ffde-997c-4482-b7fe-2524c828a188
-- ============================================

INSERT INTO rol_permission (id, rol_id, permission_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),
    '1214ffde-997c-4482-b7fe-2524c828a188',
    'a0b65172-26d5-4a5c-9c93-6fdfa9a0d46b',
    TRUE,
    NOW(),
    NOW()
);

-- ============================================
-- 6. Asignar permiso APPOINTMENTS (Gestión de Citas) al rol COLLA
-- rol_id = 4c8c2dcd-3562-4f4a-a317-c976bbc53464
-- permission_id = b1c65172-26d5-4a5c-9c93-6fdfa9a0d40a (APPOINTMENTS)
-- ============================================

INSERT INTO rol_permission (id, rol_id, permission_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),
    '4c8c2dcd-3562-4f4a-a317-c976bbc53464',
    'b1c65172-26d5-4a5c-9c93-6fdfa9a0d40a',
    TRUE,
    NOW(),
    NOW()
);

--ROLLBACK UPDATE menu SET name = 'Citas', label = 'menu.appointments', description = 'menu.appointments_description', route = '/appointments', icon = 'clock', updated_date = NOW() WHERE id = 'a0b65172-26d5-4a5c-9c93-6fdfa9a0d39f';
--ROLLBACK DELETE FROM rol_permission WHERE rol_id = '4c8c2dcd-3562-4f4a-a317-c976bbc53464' AND permission_id = 'b1c65172-26d5-4a5c-9c93-6fdfa9a0d40a';
--ROLLBACK DELETE FROM rol_permission WHERE rol_id = '1214ffde-997c-4482-b7fe-2524c828a188' AND permission_id = 'a0b65172-26d5-4a5c-9c93-6fdfa9a0d46b';
--ROLLBACK DELETE FROM menu_permission WHERE menu_id = 'a0b65172-26d5-4a5c-9c93-6fdfa9a0d46a';
--ROLLBACK DELETE FROM permission WHERE id = 'a0b65172-26d5-4a5c-9c93-6fdfa9a0d46b';
--ROLLBACK DELETE FROM menu WHERE id = 'a0b65172-26d5-4a5c-9c93-6fdfa9a0d46a';

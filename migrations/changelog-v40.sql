-- liquibase formatted sql
-- changeset insert-permission-menu-citas:1734742800000-40

-- ============================================
-- Crear permiso para el menú Citas
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
    'b1c65172-26d5-4a5c-9c93-6fdfa9a0d40a',
    NULL, 
    'APPOINTMENTS',
    'Permite al usuario acceder al menú de citas', 
    TRUE,
    NOW(),
    NOW()
);

-- ============================================
-- Crear relación menu_permission para Citas
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
    'a0b65172-26d5-4a5c-9c93-6fdfa9a0d39f',
    'b1c65172-26d5-4a5c-9c93-6fdfa9a0d40a',
    TRUE, 
    NOW(), 
    NOW()
);

--ROLLBACK DELETE FROM menu_permission WHERE menu_id = 'a0b65172-26d5-4a5c-9c93-6fdfa9a0d39f';
--ROLLBACK DELETE FROM permission WHERE id = 'b1c65172-26d5-4a5c-9c93-6fdfa9a0d40a';


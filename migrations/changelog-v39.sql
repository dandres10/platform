-- liquibase formatted sql
-- changeset insert-menu-citas:1734739200000-39

-- ============================================
-- Crear menú Citas con formato i18n
-- ============================================

-- Insertar Citas (Cabeza)
INSERT INTO menu (id, company_id, "name", "label", description, top_id, route, state, icon, created_date, updated_date) 
VALUES (
    'a0b65172-26d5-4a5c-9c93-6fdfa9a0d39f',
    NULL,
    'Citas',
    'menu.appointments',
    'menu.appointments_description',
    'a0b65172-26d5-4a5c-9c93-6fdfa9a0d39f',
    '/appointments',
    true,
    'calendar',
    now(),
    now()
);

--ROLLBACK DELETE FROM menu WHERE id = 'a0b65172-26d5-4a5c-9c93-6fdfa9a0d39f';

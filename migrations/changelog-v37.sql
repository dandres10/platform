-- liquibase formatted sql
-- changeset global-menu-permissions:1733875200000-37

-- ============================================
-- Agregar menu_permission para menús globales (company_id = NULL)
-- Esto es NECESARIO para que cuando se clone una compañía,
-- los permisos de menú también se clonen correctamente.
-- Sin esto, el login no encuentra menús para la compañía.
-- ============================================

-- ============================================
-- Traducción para error al crear currency_location
-- ============================================
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'create_company_error_creating_currency_location', 'es', 'Error al asociar la moneda con la ubicación', 'backend', true, now(), now()),
(uuid_generate_v4(), 'create_company_error_creating_currency_location', 'en', 'Error associating currency with location', 'backend', true, now(), now());

--ROLLBACK DELETE FROM menu_permission WHERE menu_id IN ('7e16d1e1-ca05-416f-8514-c7f24e9cdb3f', 'a0b65172-26d5-4a5c-9c93-6fdfa9a0d38f', 'a0b65172-26d5-4a5c-9c93-6fdfa9a0d39f', 'a0b65172-26d5-4a5c-9c93-6fdfa9a0d37f');
--ROLLBACK DELETE FROM translation WHERE "key" = 'create_company_error_creating_currency_location';


-- liquibase formatted sql
-- changeset users-internal-security-translations:1733616000000-34

-- ============================================
-- Traducciones para validación de seguridad Users Internal
-- ============================================

-- Errores de validación
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'auth_users_internal_location_required', 'es', 'El filtro location_id es requerido para consultar usuarios internos', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_users_internal_location_required', 'en', 'The location_id filter is required to query internal users', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_users_internal_location_mismatch', 'es', 'No tiene autorización para consultar usuarios de esta ubicación', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_users_internal_location_mismatch', 'en', 'You are not authorized to query users from this location', 'backend', true, now(), now());

--ROLLBACK DELETE FROM translation WHERE "key" LIKE 'auth_users_internal_%';


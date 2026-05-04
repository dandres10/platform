-- liquibase formatted sql
-- changeset spec-014-messages-i18n:1740499200000-66

-- SPEC-014 T4

--RUN

INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'auth_api_token_rol_not_found', 'es', 'El rol no existe', 'error', true, now(), now()),
(uuid_generate_v4(), 'auth_api_token_rol_not_found', 'en', 'Role not found', 'error', true, now(), now()),
(uuid_generate_v4(), 'auth_api_token_already_exists', 'es', 'El rol ya tiene un token API asociado', 'error', true, now(), now()),
(uuid_generate_v4(), 'auth_api_token_already_exists', 'en', 'Role already has an API token', 'error', true, now(), now()),
(uuid_generate_v4(), 'auth_logout_success', 'es', 'Cierre de sesión exitoso', 'success', true, now(), now()),
(uuid_generate_v4(), 'auth_logout_success', 'en', 'Logout successful', 'success', true, now(), now());

--FIN RUN

--ROLLBACK
DELETE FROM translation WHERE "key" IN (
    'auth_api_token_rol_not_found',
    'auth_api_token_already_exists',
    'auth_logout_success'
);
--FIN ROLLBACK

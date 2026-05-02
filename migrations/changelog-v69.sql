-- liquibase formatted sql
-- changeset spec-030-t2-translations:1746230400000-69

-- SPEC-030 T2

--RUN

INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'auth_login_invalid_credentials', 'es', 'Credenciales inválidas', 'error', true, now(), now()),
(uuid_generate_v4(), 'auth_login_invalid_credentials', 'en', 'Invalid credentials', 'error', true, now(), now());

--ROLLBACK
DELETE FROM translation WHERE "key" = 'auth_login_invalid_credentials';
--FIN ROLLBACK

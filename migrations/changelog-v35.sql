-- liquibase formatted sql
-- changeset delete-user-internal-last-admin:1733702400000-35

-- ============================================
-- Traducción para validación de último admin
-- ============================================

INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'auth_delete_user_last_admin', 'es', 'Este usuario es el único administrador de esta ubicación. Debe crear o asignar rol de administrador a otro usuario antes de poder eliminarlo', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_last_admin', 'en', 'This user is the only administrator for this location. You must create or assign the administrator role to another user before you can delete this one', 'backend', true, now(), now());

--ROLLBACK DELETE FROM translation WHERE "key" = 'auth_delete_user_last_admin';


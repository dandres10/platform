-- liquibase formatted sql
-- changeset update-user-internal-translations:1733788800000-36

-- ============================================
-- Traducciones para flujo Update User Internal
-- ============================================

-- Errores de validación
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'auth_update_user_not_found', 'es', 'El usuario con ID {user_id} no existe en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_update_user_not_found', 'en', 'The user with ID {user_id} does not exist in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_update_user_not_in_location', 'es', 'El usuario no pertenece a su ubicación', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_update_user_not_in_location', 'en', 'The user does not belong to your location', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_update_user_cannot_demote_self', 'es', 'No puede quitarse el rol de administrador a sí mismo', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_update_user_cannot_demote_self', 'en', 'You cannot remove the administrator role from yourself', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_update_user_last_admin', 'es', 'Este usuario es el único administrador de la ubicación. Debe asignar rol de administrador a otro usuario primero', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_update_user_last_admin', 'en', 'This user is the only administrator for this location. You must assign the administrator role to another user first', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_update_user_rol_not_found', 'es', 'El rol especificado no existe', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_update_user_rol_not_found', 'en', 'The specified role does not exist', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_update_user_error_fetching_roles', 'es', 'Error al obtener los roles del usuario', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_update_user_error_fetching_roles', 'en', 'Error fetching user roles', 'backend', true, now(), now());

-- Errores de proceso
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'auth_update_user_error', 'es', 'Error al actualizar el usuario', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_update_user_error', 'en', 'Error updating user', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_update_user_error_updating_rol', 'es', 'Error al actualizar el rol del usuario', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_update_user_error_updating_rol', 'en', 'Error updating user role', 'backend', true, now(), now());

-- Éxito
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'auth_update_user_success', 'es', 'Usuario interno actualizado exitosamente', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_update_user_success', 'en', 'Internal user updated successfully', 'backend', true, now(), now());

--ROLLBACK DELETE FROM translation WHERE "key" LIKE 'auth_update_user_%';


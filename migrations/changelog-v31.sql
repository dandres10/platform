-- liquibase formatted sql
-- changeset delete-user-internal-translations:1733356800000-31

-- ============================================
-- Traducciones para flujo Delete User Internal
-- ============================================

-- Errores de validación
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'auth_delete_user_not_found', 'es', 'El usuario con ID {user_id} no existe en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_not_found', 'en', 'The user with ID {user_id} does not exist in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_delete_user_cannot_delete_self', 'es', 'No puede eliminar su propio usuario', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_cannot_delete_self', 'en', 'You cannot delete your own user', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_delete_user_has_active_relations', 'es', 'El usuario está relacionado a flujos activos y no puede ser eliminado', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_has_active_relations', 'en', 'The user is related to active flows and cannot be deleted', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_delete_user_not_in_location', 'es', 'El usuario no pertenece a su ubicación y no puede ser eliminado', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_not_in_location', 'en', 'The user does not belong to your location and cannot be deleted', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_delete_user_error_fetching_roles', 'es', 'Error al obtener los roles del usuario', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_error_fetching_roles', 'en', 'Error fetching user roles', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_delete_user_no_roles_found', 'es', 'El usuario no tiene roles asignados. Esto indica un problema de integridad de datos', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_no_roles_found', 'en', 'The user has no assigned roles. This indicates a data integrity issue', 'backend', true, now(), now());

-- Errores de proceso
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'auth_delete_user_error_deleting_roles', 'es', 'Error al eliminar las asignaciones de rol del usuario', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_error_deleting_roles', 'en', 'Error deleting user role assignments', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_delete_user_error_deleting_user', 'es', 'Error al eliminar el usuario', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_error_deleting_user', 'en', 'Error deleting user', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_delete_user_error_deleting_platform', 'es', 'Error al eliminar la configuración de plataforma', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_error_deleting_platform', 'en', 'Error deleting platform configuration', 'backend', true, now(), now());

-- Soft delete (inactivación)
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'auth_delete_user_soft_deleted', 'es', 'El usuario tiene relaciones activas y no pudo ser eliminado, pero fue inactivado. Será eliminado permanentemente después de 1 mes', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_soft_deleted', 'en', 'The user has active relations and could not be deleted, but was deactivated. It will be permanently deleted after 1 month', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_delete_user_error_soft_delete', 'es', 'Error al inactivar el usuario', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_error_soft_delete', 'en', 'Error deactivating user', 'backend', true, now(), now());

-- Éxito
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'auth_delete_user_success', 'es', 'Usuario interno eliminado exitosamente', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_success', 'en', 'Internal user deleted successfully', 'backend', true, now(), now());

--ROLLBACK DELETE FROM translation WHERE "key" LIKE 'auth_delete_user_%';


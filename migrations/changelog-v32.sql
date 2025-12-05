-- liquibase formatted sql
-- changeset delete-user-external-translations:1733443200000-32

-- ============================================
-- Traducciones para flujo Delete User External
-- ============================================

-- Errores de validación
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'auth_delete_user_external_not_found', 'es', 'El usuario con ID {user_id} no existe en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_external_not_found', 'en', 'The user with ID {user_id} does not exist in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_delete_user_external_unauthorized', 'es', 'No tiene autorización para eliminar este usuario', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_external_unauthorized', 'en', 'You are not authorized to delete this user', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_delete_user_external_has_active_relations', 'es', 'El usuario está relacionado a flujos activos y no puede ser eliminado', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_external_has_active_relations', 'en', 'The user is related to active flows and cannot be deleted', 'backend', true, now(), now());

-- Errores de proceso
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'auth_delete_user_external_error_deleting_user', 'es', 'Error al eliminar el usuario', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_external_error_deleting_user', 'en', 'Error deleting user', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_delete_user_external_error_deleting_platform', 'es', 'Error al eliminar la configuración de plataforma', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_external_error_deleting_platform', 'en', 'Error deleting platform configuration', 'backend', true, now(), now());

-- Soft delete (inactivación)
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'auth_delete_user_external_soft_deleted', 'es', 'Tu cuenta tiene relaciones activas y no pudo ser eliminada, pero fue inactivada. Será eliminada permanentemente después de 1 mes', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_external_soft_deleted', 'en', 'Your account has active relations and could not be deleted, but was deactivated. It will be permanently deleted after 1 month', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_delete_user_external_error_soft_delete', 'es', 'Error al inactivar tu cuenta', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_external_error_soft_delete', 'en', 'Error deactivating your account', 'backend', true, now(), now());

-- Éxito
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'auth_delete_user_external_success', 'es', 'Usuario externo eliminado exitosamente', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_delete_user_external_success', 'en', 'External user deleted successfully', 'backend', true, now(), now());

--ROLLBACK DELETE FROM translation WHERE "key" LIKE 'auth_delete_user_external_%';


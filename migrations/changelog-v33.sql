-- liquibase formatted sql
-- changeset delete-company-translations:1733529600000-33

-- ============================================
-- Traducciones para flujo Delete Company
-- ============================================

-- Errores de validación
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'delete_company_not_found', 'es', 'La compañía con ID {company_id} no existe en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'delete_company_not_found', 'en', 'The company with ID {company_id} does not exist in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'delete_company_unauthorized', 'es', 'No tiene autorización para eliminar esta compañía', 'backend', true, now(), now()),
(uuid_generate_v4(), 'delete_company_unauthorized', 'en', 'You are not authorized to delete this company', 'backend', true, now(), now()),

(uuid_generate_v4(), 'delete_company_has_active_relations', 'es', 'La compañía tiene relaciones activas y no puede ser eliminada', 'backend', true, now(), now()),
(uuid_generate_v4(), 'delete_company_has_active_relations', 'en', 'The company has active relations and cannot be deleted', 'backend', true, now(), now());

-- Errores de proceso
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'delete_company_error_deleting_users', 'es', 'Error al eliminar los usuarios de la compañía', 'backend', true, now(), now()),
(uuid_generate_v4(), 'delete_company_error_deleting_users', 'en', 'Error deleting company users', 'backend', true, now(), now()),

(uuid_generate_v4(), 'delete_company_error_deleting_menus', 'es', 'Error al eliminar los menús de la compañía', 'backend', true, now(), now()),
(uuid_generate_v4(), 'delete_company_error_deleting_menus', 'en', 'Error deleting company menus', 'backend', true, now(), now()),

(uuid_generate_v4(), 'delete_company_error_deleting_locations', 'es', 'Error al eliminar las ubicaciones de la compañía', 'backend', true, now(), now()),
(uuid_generate_v4(), 'delete_company_error_deleting_locations', 'en', 'Error deleting company locations', 'backend', true, now(), now()),

(uuid_generate_v4(), 'delete_company_error_deleting_company', 'es', 'Error al eliminar la compañía', 'backend', true, now(), now()),
(uuid_generate_v4(), 'delete_company_error_deleting_company', 'en', 'Error deleting company', 'backend', true, now(), now());

-- Soft delete (inactivación)
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'delete_company_soft_deleted', 'es', 'La compañía tiene relaciones activas y no pudo ser eliminada, pero fue inactivada. Será eliminada permanentemente después de 1 mes', 'backend', true, now(), now()),
(uuid_generate_v4(), 'delete_company_soft_deleted', 'en', 'The company has active relations and could not be deleted, but was deactivated. It will be permanently deleted after 1 month', 'backend', true, now(), now()),

(uuid_generate_v4(), 'delete_company_error_soft_delete', 'es', 'Error al inactivar la compañía', 'backend', true, now(), now()),
(uuid_generate_v4(), 'delete_company_error_soft_delete', 'en', 'Error deactivating company', 'backend', true, now(), now());

-- Éxito
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'delete_company_success', 'es', 'Compañía eliminada exitosamente', 'backend', true, now(), now()),
(uuid_generate_v4(), 'delete_company_success', 'en', 'Company deleted successfully', 'backend', true, now(), now());

--ROLLBACK DELETE FROM translation WHERE "key" LIKE 'delete_company_%';


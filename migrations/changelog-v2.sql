INSERT INTO "translation" (id, "key", language_code, "translation", context, state, created_date, updated_date) values 

(uuid_generate_v4(), 'core_query_made', 'es', 'consulta realizada', 'backend', true, now(), now()),
(uuid_generate_v4(), 'core_query_made', 'en', 'query made', 'backend', true, now(), now()),

(uuid_generate_v4(), 'core_saved_information', 'es', 'información guarda', 'backend', true, now(), now()),
(uuid_generate_v4(), 'core_saved_information', 'en', 'saved information', 'backend', true, now(), now()),

(uuid_generate_v4(), 'core_updated_information', 'es', 'información actualizada', 'backend', true, now(), now()),
(uuid_generate_v4(), 'core_updated_information', 'en', 'updated information', 'backend', true, now(), now()),

(uuid_generate_v4(), 'core_deletion_performed', 'es', 'eliminación realizada', 'backend', true, now(), now()),
(uuid_generate_v4(), 'core_deletion_performed', 'en', 'deletion performed', 'backend', true, now(), now()),

(uuid_generate_v4(), 'core_record_not_found_to_delete', 'es', 'no se encontró el registro a eliminar', 'backend', true, now(), now()),
(uuid_generate_v4(), 'core_record_not_found_to_delete', 'en', 'record not found to delete', 'backend', true, now(), now()),

(uuid_generate_v4(), 'core_no_results_found', 'es', 'no se encontraron resultados', 'backend', true, now(), now()),
(uuid_generate_v4(), 'core_no_results_found', 'en', 'no results found', 'backend', true, now(), now()),

(uuid_generate_v4(), 'core_record_not_found', 'es', 'no se encontró el registro', 'backend', true, now(), now()),
(uuid_generate_v4(), 'core_record_not_found', 'en', 'record not found', 'backend', true, now(), now()),

(uuid_generate_v4(), 'core_error_saving_record', 'es', 'Error al guardar el registro', 'backend', true, now(), now()),
(uuid_generate_v4(), 'core_error_saving_record', 'en', 'Error saving the record', 'backend', true, now(), now()),

(uuid_generate_v4(), 'core_update_failed', 'es', 'no se pudo realizar la actualización', 'backend', true, now(), now()),
(uuid_generate_v4(), 'core_update_failed', 'en', 'the update could not be completed', 'backend', true, now(), now());

--rollback


DELETE FROM "translation"
WHERE "key" IN (
    'core_query_made',
    'core_saved_information',
    'core_updated_information',
    'core_deletion_performed',
    'core_record_not_found_to_delete',
    'core_no_results_found',
    'core_record_not_found',
    'core_error_saving_record',
    'core_update_failed'
);

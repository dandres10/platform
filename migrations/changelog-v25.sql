-- liquibase formatted sql
-- changeset create-user-internal-flow:1731187200000-25 insert translations for create user internal endpoint

INSERT INTO "translation" (id, "key", language_code, "translation", context, state, created_date, updated_date) values 

(uuid_generate_v4(), 'auth_create_user_language_not_found', 'es', 'El idioma especificado no existe en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_create_user_language_not_found', 'en', 'The specified language does not exist in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_create_user_currency_not_found', 'es', 'La moneda especificada no existe en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_create_user_currency_not_found', 'en', 'The specified currency does not exist in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_create_user_empty_location_rol', 'es', 'Debe proporcionar al menos una asignación de rol y ubicación', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_create_user_empty_location_rol', 'en', 'You must provide at least one role and location assignment', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_create_user_location_not_found', 'es', 'La ubicación con ID {location_id} no existe en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_create_user_location_not_found', 'en', 'The location with ID {location_id} does not exist in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_create_user_rol_not_found', 'es', 'El rol con ID {rol_id} no existe en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_create_user_rol_not_found', 'en', 'The role with ID {rol_id} does not exist in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_create_user_duplicate_combination', 'es', 'La combinación de location_id y rol_id está duplicada en la lista', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_create_user_duplicate_combination', 'en', 'The combination of location_id and rol_id is duplicated in the list', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_create_user_email_already_exists', 'es', 'El email ya está registrado en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_create_user_email_already_exists', 'en', 'The email is already registered in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_create_user_success', 'es', 'Usuario interno creado exitosamente', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_create_user_success', 'en', 'Internal user created successfully', 'backend', true, now(), now());


-- liquibase formatted sql
-- changeset create-user-external-flow:1731188500000-27 insert translations for create user external endpoint

INSERT INTO "translation" (id, "key", language_code, "translation", context, state, created_date, updated_date) values 

(uuid_generate_v4(), 'auth_create_user_external_language_not_found', 'es', 'El idioma especificado no existe en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_create_user_external_language_not_found', 'en', 'The specified language does not exist in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_create_user_external_currency_not_found', 'es', 'La moneda especificada no existe en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_create_user_external_currency_not_found', 'en', 'The specified currency does not exist in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_create_user_external_email_already_exists', 'es', 'El email ya está registrado en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_create_user_external_email_already_exists', 'en', 'The email is already registered in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_create_user_external_identification_already_exists', 'es', 'La identificación ya está registrada en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_create_user_external_identification_already_exists', 'en', 'The identification is already registered in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'auth_create_user_external_success', 'es', 'Usuario externo creado exitosamente', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_create_user_external_success', 'en', 'External user created successfully', 'backend', true, now(), now());


-- liquibase formatted sql
-- changeset create-company-translations:1731445300000-30

-- ============================================
-- Traducciones para flujo Create Company
-- ============================================

-- Errores de validación
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'create_company_nit_already_exists', 'es', 'El NIT ya está registrado en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'create_company_nit_already_exists', 'en', 'The NIT is already registered in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'create_company_email_already_exists', 'es', 'El email ya está registrado en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'create_company_email_already_exists', 'en', 'The email is already registered in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'create_company_country_not_found', 'es', 'El país especificado no existe en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'create_company_country_not_found', 'en', 'The specified country does not exist in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'create_company_language_not_found', 'es', 'El idioma especificado no existe en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'create_company_language_not_found', 'en', 'The specified language does not exist in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'create_company_currency_not_found', 'es', 'La moneda especificada no existe en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'create_company_currency_not_found', 'en', 'The specified currency does not exist in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'create_company_rol_not_found', 'es', 'El rol especificado no existe en el sistema', 'backend', true, now(), now()),
(uuid_generate_v4(), 'create_company_rol_not_found', 'en', 'The specified role does not exist in the system', 'backend', true, now(), now()),

(uuid_generate_v4(), 'create_company_no_menu_templates', 'es', 'No existe plantilla de menús en el sistema. Contacte al administrador.', 'backend', true, now(), now()),
(uuid_generate_v4(), 'create_company_no_menu_templates', 'en', 'No menu templates exist in the system. Contact the administrator.', 'backend', true, now(), now());

-- Errores de proceso
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'create_company_error_cloning_menus', 'es', 'Error al clonar los menús. Todos los cambios han sido revertidos.', 'backend', true, now(), now()),
(uuid_generate_v4(), 'create_company_error_cloning_menus', 'en', 'Error cloning menus. All changes have been rolled back.', 'backend', true, now(), now()),

(uuid_generate_v4(), 'create_company_error_creating_location', 'es', 'Error al crear la ubicación. Todos los cambios han sido revertidos.', 'backend', true, now(), now()),
(uuid_generate_v4(), 'create_company_error_creating_location', 'en', 'Error creating location. All changes have been rolled back.', 'backend', true, now(), now()),

(uuid_generate_v4(), 'create_company_error_creating_admin', 'es', 'Error al crear el usuario administrador. Todos los cambios han sido revertidos.', 'backend', true, now(), now()),
(uuid_generate_v4(), 'create_company_error_creating_admin', 'en', 'Error creating admin user. All changes have been rolled back.', 'backend', true, now(), now());

-- Éxito
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'create_company_success', 'es', 'Compañía creada exitosamente', 'backend', true, now(), now()),
(uuid_generate_v4(), 'create_company_success', 'en', 'Company created successfully', 'backend', true, now(), now());

-- reCAPTCHA (Opcional - para uso futuro)
INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'create_company_recaptcha_failed', 'es', 'Verificación de seguridad fallida. Por favor intente nuevamente.', 'backend', true, now(), now()),
(uuid_generate_v4(), 'create_company_recaptcha_failed', 'en', 'Security verification failed. Please try again.', 'backend', true, now(), now());

--ROLLBACK DELETE FROM translation WHERE "key" LIKE 'create_company_%';


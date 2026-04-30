-- liquibase formatted sql
-- changeset spec-001-company-currency-translations:1740412800000-65

-- SPEC-001 T6.7

--RUN

INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'plt_company_currency_duplicate', 'es', 'La moneda ya está asociada a esta empresa', 'error', true, now(), now()),
(uuid_generate_v4(), 'plt_company_currency_duplicate', 'en', 'Currency is already associated with this company', 'error', true, now(), now()),
(uuid_generate_v4(), 'plt_company_currency_base_already_exists', 'es', 'Ya existe una moneda base para esta empresa', 'error', true, now(), now()),
(uuid_generate_v4(), 'plt_company_currency_base_already_exists', 'en', 'A base currency already exists for this company', 'error', true, now(), now()),
(uuid_generate_v4(), 'plt_company_currency_base_required', 'es', 'La empresa debe tener al menos una moneda base; reasigna otra como base antes de eliminarla', 'error', true, now(), now()),
(uuid_generate_v4(), 'plt_company_currency_base_required', 'en', 'Company must have at least one base currency; reassign another as base before deleting', 'error', true, now(), now()),
(uuid_generate_v4(), 'plt_currency_not_allowed_for_company', 'es', 'Esta moneda no está habilitada para la empresa', 'error', true, now(), now()),
(uuid_generate_v4(), 'plt_currency_not_allowed_for_company', 'en', 'This currency is not enabled for the company', 'error', true, now(), now()),
(uuid_generate_v4(), 'plt_company_currency_not_found', 'es', 'No se encontró la asociación de moneda solicitada', 'error', true, now(), now()),
(uuid_generate_v4(), 'plt_company_currency_not_found', 'en', 'Requested currency association not found', 'error', true, now(), now()),
(uuid_generate_v4(), 'plt_company_currency_first_must_be_base', 'es', 'La primera moneda registrada para una empresa debe ser la moneda base', 'error', true, now(), now()),
(uuid_generate_v4(), 'plt_company_currency_first_must_be_base', 'en', 'The first currency registered for a company must be the base currency', 'error', true, now(), now());

--FIN RUN

--ROLLBACK
DELETE FROM translation WHERE "key" IN (
    'plt_company_currency_duplicate',
    'plt_company_currency_base_already_exists',
    'plt_company_currency_base_required',
    'plt_currency_not_allowed_for_company',
    'plt_company_currency_not_found',
    'plt_company_currency_first_must_be_base'
);
--FIN ROLLBACK

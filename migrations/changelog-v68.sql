-- liquibase formatted sql
-- changeset spec-004-d6-translations:1740672000000-68

-- SPEC-004 D6

--RUN

INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
(uuid_generate_v4(), 'plt_geo_phone_code_only_country', 'es', 'El código telefónico solo aplica a países', 'error', true, now(), now()),
(uuid_generate_v4(), 'plt_geo_phone_code_only_country', 'en', 'Phone code is only applicable to countries', 'error', true, now(), now());

--FIN RUN

--ROLLBACK
DELETE FROM translation WHERE "key" = 'plt_geo_phone_code_only_country';
--FIN ROLLBACK

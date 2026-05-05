-- liquibase formatted sql
-- changeset spec-033-timezone-aware-columns:1746489600000-73

-- SPEC-033 T2

-- ============================================
-- MIGRACION: Convertir columnas TIMESTAMP → TIMESTAMPTZ
--
-- Paridad con chat (referencia canónica). Usa current_setting('timezone')
-- en el USING para que la conversión sea portable: el server local
-- (America/Bogota) interpreta los timestamps como Bogota; prod (UTC) los
-- interpreta como UTC. Resultado: TIMESTAMPTZ correcto en cualquier
-- ambiente sin cambiar el SQL.
--
-- 41 columnas en 19 tablas de business + auth. Excluye migration_history
-- (tabla interna del sistema de migraciones, mantiene el formato actual).
-- ============================================

--RUN

-- 1. api_token
ALTER TABLE "api_token" ALTER COLUMN created_date TYPE TIMESTAMPTZ USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "api_token" ALTER COLUMN updated_date TYPE TIMESTAMPTZ USING updated_date AT TIME ZONE current_setting('timezone');

-- 2. company
ALTER TABLE "company" ALTER COLUMN created_date TYPE TIMESTAMPTZ USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "company" ALTER COLUMN updated_date TYPE TIMESTAMPTZ USING updated_date AT TIME ZONE current_setting('timezone');

-- 3. company_currency
ALTER TABLE "company_currency" ALTER COLUMN created_date TYPE TIMESTAMPTZ USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "company_currency" ALTER COLUMN updated_date TYPE TIMESTAMPTZ USING updated_date AT TIME ZONE current_setting('timezone');

-- 4. currency
ALTER TABLE "currency" ALTER COLUMN created_date TYPE TIMESTAMPTZ USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "currency" ALTER COLUMN updated_date TYPE TIMESTAMPTZ USING updated_date AT TIME ZONE current_setting('timezone');

-- 5. currency_location
ALTER TABLE "currency_location" ALTER COLUMN created_date TYPE TIMESTAMPTZ USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "currency_location" ALTER COLUMN updated_date TYPE TIMESTAMPTZ USING updated_date AT TIME ZONE current_setting('timezone');

-- 6. geo_division
ALTER TABLE "geo_division" ALTER COLUMN created_date TYPE TIMESTAMPTZ USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "geo_division" ALTER COLUMN updated_date TYPE TIMESTAMPTZ USING updated_date AT TIME ZONE current_setting('timezone');

-- 7. geo_division_type
ALTER TABLE "geo_division_type" ALTER COLUMN created_date TYPE TIMESTAMPTZ USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "geo_division_type" ALTER COLUMN updated_date TYPE TIMESTAMPTZ USING updated_date AT TIME ZONE current_setting('timezone');

-- 8. language
ALTER TABLE "language" ALTER COLUMN created_date TYPE TIMESTAMPTZ USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "language" ALTER COLUMN updated_date TYPE TIMESTAMPTZ USING updated_date AT TIME ZONE current_setting('timezone');

-- 9. location
ALTER TABLE "location" ALTER COLUMN created_date TYPE TIMESTAMPTZ USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "location" ALTER COLUMN updated_date TYPE TIMESTAMPTZ USING updated_date AT TIME ZONE current_setting('timezone');

-- 10. menu
ALTER TABLE "menu" ALTER COLUMN created_date TYPE TIMESTAMPTZ USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "menu" ALTER COLUMN updated_date TYPE TIMESTAMPTZ USING updated_date AT TIME ZONE current_setting('timezone');

-- 11. menu_permission
ALTER TABLE "menu_permission" ALTER COLUMN created_date TYPE TIMESTAMPTZ USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "menu_permission" ALTER COLUMN updated_date TYPE TIMESTAMPTZ USING updated_date AT TIME ZONE current_setting('timezone');

-- 12. password_reset_token (T4 SPEC-006)
ALTER TABLE "password_reset_token" ALTER COLUMN created_date TYPE TIMESTAMPTZ USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "password_reset_token" ALTER COLUMN updated_date TYPE TIMESTAMPTZ USING updated_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "password_reset_token" ALTER COLUMN expires_at TYPE TIMESTAMPTZ USING expires_at AT TIME ZONE current_setting('timezone');
ALTER TABLE "password_reset_token" ALTER COLUMN used_at TYPE TIMESTAMPTZ USING used_at AT TIME ZONE current_setting('timezone');

-- 13. permission
ALTER TABLE "permission" ALTER COLUMN created_date TYPE TIMESTAMPTZ USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "permission" ALTER COLUMN updated_date TYPE TIMESTAMPTZ USING updated_date AT TIME ZONE current_setting('timezone');

-- 14. platform
ALTER TABLE "platform" ALTER COLUMN created_date TYPE TIMESTAMPTZ USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "platform" ALTER COLUMN updated_date TYPE TIMESTAMPTZ USING updated_date AT TIME ZONE current_setting('timezone');

-- 15. rol
ALTER TABLE "rol" ALTER COLUMN created_date TYPE TIMESTAMPTZ USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "rol" ALTER COLUMN updated_date TYPE TIMESTAMPTZ USING updated_date AT TIME ZONE current_setting('timezone');

-- 16. rol_permission
ALTER TABLE "rol_permission" ALTER COLUMN created_date TYPE TIMESTAMPTZ USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "rol_permission" ALTER COLUMN updated_date TYPE TIMESTAMPTZ USING updated_date AT TIME ZONE current_setting('timezone');

-- 17. translation
ALTER TABLE "translation" ALTER COLUMN created_date TYPE TIMESTAMPTZ USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "translation" ALTER COLUMN updated_date TYPE TIMESTAMPTZ USING updated_date AT TIME ZONE current_setting('timezone');

-- 18. user (T10 SPEC-006: password_changed_at)
ALTER TABLE "user" ALTER COLUMN created_date TYPE TIMESTAMPTZ USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "user" ALTER COLUMN updated_date TYPE TIMESTAMPTZ USING updated_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "user" ALTER COLUMN password_changed_at TYPE TIMESTAMPTZ USING password_changed_at AT TIME ZONE current_setting('timezone');

-- 19. user_country
ALTER TABLE "user_country" ALTER COLUMN created_date TYPE TIMESTAMPTZ USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "user_country" ALTER COLUMN updated_date TYPE TIMESTAMPTZ USING updated_date AT TIME ZONE current_setting('timezone');

-- 20. user_location_rol
ALTER TABLE "user_location_rol" ALTER COLUMN created_date TYPE TIMESTAMPTZ USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "user_location_rol" ALTER COLUMN updated_date TYPE TIMESTAMPTZ USING updated_date AT TIME ZONE current_setting('timezone');

--FIN RUN

--ROLLBACK
-- Reverse: TIMESTAMPTZ → TIMESTAMP. Mismo patrón usando current_setting('timezone').
-- 1. api_token
ALTER TABLE "api_token" ALTER COLUMN created_date TYPE TIMESTAMP USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "api_token" ALTER COLUMN updated_date TYPE TIMESTAMP USING updated_date AT TIME ZONE current_setting('timezone');
-- 2. company
ALTER TABLE "company" ALTER COLUMN created_date TYPE TIMESTAMP USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "company" ALTER COLUMN updated_date TYPE TIMESTAMP USING updated_date AT TIME ZONE current_setting('timezone');
-- 3. company_currency
ALTER TABLE "company_currency" ALTER COLUMN created_date TYPE TIMESTAMP USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "company_currency" ALTER COLUMN updated_date TYPE TIMESTAMP USING updated_date AT TIME ZONE current_setting('timezone');
-- 4. currency
ALTER TABLE "currency" ALTER COLUMN created_date TYPE TIMESTAMP USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "currency" ALTER COLUMN updated_date TYPE TIMESTAMP USING updated_date AT TIME ZONE current_setting('timezone');
-- 5. currency_location
ALTER TABLE "currency_location" ALTER COLUMN created_date TYPE TIMESTAMP USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "currency_location" ALTER COLUMN updated_date TYPE TIMESTAMP USING updated_date AT TIME ZONE current_setting('timezone');
-- 6. geo_division
ALTER TABLE "geo_division" ALTER COLUMN created_date TYPE TIMESTAMP USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "geo_division" ALTER COLUMN updated_date TYPE TIMESTAMP USING updated_date AT TIME ZONE current_setting('timezone');
-- 7. geo_division_type
ALTER TABLE "geo_division_type" ALTER COLUMN created_date TYPE TIMESTAMP USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "geo_division_type" ALTER COLUMN updated_date TYPE TIMESTAMP USING updated_date AT TIME ZONE current_setting('timezone');
-- 8. language
ALTER TABLE "language" ALTER COLUMN created_date TYPE TIMESTAMP USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "language" ALTER COLUMN updated_date TYPE TIMESTAMP USING updated_date AT TIME ZONE current_setting('timezone');
-- 9. location
ALTER TABLE "location" ALTER COLUMN created_date TYPE TIMESTAMP USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "location" ALTER COLUMN updated_date TYPE TIMESTAMP USING updated_date AT TIME ZONE current_setting('timezone');
-- 10. menu
ALTER TABLE "menu" ALTER COLUMN created_date TYPE TIMESTAMP USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "menu" ALTER COLUMN updated_date TYPE TIMESTAMP USING updated_date AT TIME ZONE current_setting('timezone');
-- 11. menu_permission
ALTER TABLE "menu_permission" ALTER COLUMN created_date TYPE TIMESTAMP USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "menu_permission" ALTER COLUMN updated_date TYPE TIMESTAMP USING updated_date AT TIME ZONE current_setting('timezone');
-- 12. password_reset_token
ALTER TABLE "password_reset_token" ALTER COLUMN created_date TYPE TIMESTAMP USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "password_reset_token" ALTER COLUMN updated_date TYPE TIMESTAMP USING updated_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "password_reset_token" ALTER COLUMN expires_at TYPE TIMESTAMP USING expires_at AT TIME ZONE current_setting('timezone');
ALTER TABLE "password_reset_token" ALTER COLUMN used_at TYPE TIMESTAMP USING used_at AT TIME ZONE current_setting('timezone');
-- 13. permission
ALTER TABLE "permission" ALTER COLUMN created_date TYPE TIMESTAMP USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "permission" ALTER COLUMN updated_date TYPE TIMESTAMP USING updated_date AT TIME ZONE current_setting('timezone');
-- 14. platform
ALTER TABLE "platform" ALTER COLUMN created_date TYPE TIMESTAMP USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "platform" ALTER COLUMN updated_date TYPE TIMESTAMP USING updated_date AT TIME ZONE current_setting('timezone');
-- 15. rol
ALTER TABLE "rol" ALTER COLUMN created_date TYPE TIMESTAMP USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "rol" ALTER COLUMN updated_date TYPE TIMESTAMP USING updated_date AT TIME ZONE current_setting('timezone');
-- 16. rol_permission
ALTER TABLE "rol_permission" ALTER COLUMN created_date TYPE TIMESTAMP USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "rol_permission" ALTER COLUMN updated_date TYPE TIMESTAMP USING updated_date AT TIME ZONE current_setting('timezone');
-- 17. translation
ALTER TABLE "translation" ALTER COLUMN created_date TYPE TIMESTAMP USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "translation" ALTER COLUMN updated_date TYPE TIMESTAMP USING updated_date AT TIME ZONE current_setting('timezone');
-- 18. user
ALTER TABLE "user" ALTER COLUMN created_date TYPE TIMESTAMP USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "user" ALTER COLUMN updated_date TYPE TIMESTAMP USING updated_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "user" ALTER COLUMN password_changed_at TYPE TIMESTAMP USING password_changed_at AT TIME ZONE current_setting('timezone');
-- 19. user_country
ALTER TABLE "user_country" ALTER COLUMN created_date TYPE TIMESTAMP USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "user_country" ALTER COLUMN updated_date TYPE TIMESTAMP USING updated_date AT TIME ZONE current_setting('timezone');
-- 20. user_location_rol
ALTER TABLE "user_location_rol" ALTER COLUMN created_date TYPE TIMESTAMP USING created_date AT TIME ZONE current_setting('timezone');
ALTER TABLE "user_location_rol" ALTER COLUMN updated_date TYPE TIMESTAMP USING updated_date AT TIME ZONE current_setting('timezone');
--FIN ROLLBACK

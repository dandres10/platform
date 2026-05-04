-- liquibase formatted sql
-- changeset spec-006-t10-password-changed-at:1746662400000-72

-- SPEC-006 T10

-- ============================================
-- MIGRACION: Añadir password_changed_at a user
--
-- Columna para marcar el momento del último cambio de password.
-- Token.create_access_token incluye este timestamp en el payload
-- JWT; validate_has_refresh_token rechaza JWTs cuyo
-- password_changed_at sea menor al actual del user (= JWT
-- emitido antes del cambio = comprometido).
--
-- Tablas afectadas:
-- 1. user (ALTER TABLE ADD COLUMN)
-- ============================================

--RUN

ALTER TABLE "user" ADD COLUMN IF NOT EXISTS password_changed_at TIMESTAMP NULL;

--FIN RUN

--ROLLBACK
ALTER TABLE "user" DROP COLUMN IF EXISTS password_changed_at;
--FIN ROLLBACK

-- liquibase formatted sql
-- changeset spec-006-t4-password-reset-token:1746489600000-70

-- SPEC-006 T4

-- ============================================
-- MIGRACION: Crear tabla password_reset_token
--
-- Storage de tokens de reset de password (UUID4 random,
-- TTL 1 hora). Una fila por solicitud forgot_password.
-- Marcada used_at cuando reset_password se completa.
--
-- Tablas afectadas:
-- 1. password_reset_token (CREATE)
-- ============================================

--RUN

CREATE TABLE IF NOT EXISTS password_reset_token (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    token VARCHAR(64) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP NULL,
    state BOOLEAN NOT NULL DEFAULT TRUE,
    created_date TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_date TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_password_reset_token_token
    ON password_reset_token (token);

CREATE INDEX IF NOT EXISTS idx_password_reset_token_user_active
    ON password_reset_token (user_id)
    WHERE used_at IS NULL;

--FIN RUN

--ROLLBACK
DROP INDEX IF EXISTS idx_password_reset_token_user_active;
DROP INDEX IF EXISTS idx_password_reset_token_token;
DROP TABLE IF EXISTS password_reset_token;
--FIN ROLLBACK

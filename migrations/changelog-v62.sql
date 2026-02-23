-- liquibase formatted sql
-- changeset actions-db-migration-history:1740153600000-62

-- ============================================
-- MIGRACION: Crear tabla migration_history
--
-- Tabla de tracking para registrar qué migraciones
-- se ejecutaron y en qué ambiente (env).
--
-- Tablas afectadas:
-- 1. migration_history (CREATE)
-- ============================================

--RUN

CREATE TABLE IF NOT EXISTS migration_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    version INTEGER NOT NULL,
    env VARCHAR(20) NOT NULL,
    action VARCHAR(10) NOT NULL,
    executed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    filename VARCHAR(200) NOT NULL
);

--FIN RUN

--ROLLBACK
DROP TABLE IF EXISTS migration_history;
--FIN ROLLBACK

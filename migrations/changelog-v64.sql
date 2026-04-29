-- liquibase formatted sql
-- changeset add-company-currency:1740326400000-64

-- ============================================
-- MIGRACION: Crear tabla company_currency
--
-- Tabla para asociar currencies a companies y marcar
-- la moneda base por compania (is_base = true).
--
-- Reglas:
-- - UNIQUE (company_id, currency_id): no duplicar currency por compania.
-- - Partial unique index: solo una moneda base por compania.
--
-- Tablas afectadas:
-- 1. company_currency (CREATE)
-- 2. idx_company_currency_one_base (CREATE)
-- ============================================

--RUN

CREATE TABLE IF NOT EXISTS company_currency (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES company (id),
    currency_id UUID NOT NULL REFERENCES currency (id),
    is_base BOOLEAN NOT NULL DEFAULT FALSE,
    state BOOLEAN NOT NULL DEFAULT TRUE,
    created_date TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_date TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT company_currency_unique UNIQUE (company_id, currency_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_company_currency_one_base
    ON company_currency (company_id)
    WHERE is_base = TRUE;

--FIN RUN

--ROLLBACK
DROP INDEX IF EXISTS idx_company_currency_one_base;
DROP TABLE IF EXISTS company_currency;
--FIN ROLLBACK

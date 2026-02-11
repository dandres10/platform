-- liquibase formatted sql
-- changeset drop-country-table:1737050800000-59

-- ============================================
-- MIGRACIÓN: Eliminar tabla country
--
-- La tabla country ya no es necesaria.
-- Los países ahora son nodos raíz en geo_division
-- (level = 0, top_id = NULL, type = COUNTRY).
--
-- Pre-requisitos:
-- - changelog-v53.sql: Colombia migrada a geo_division
-- - changelog-v57.sql: location.country_id apunta a geo_division
-- - changelog-v58.sql: user_country.country_id apunta a geo_division
--
-- Con estos cambios, la tabla country ya no tiene
-- FKs que la referencien y se puede eliminar de forma segura.
--
-- Tablas afectadas:
-- 1. country (DROP)
-- ============================================

-- ============================================
-- 1. Eliminar tabla country
-- ============================================

DROP TABLE IF EXISTS country;

-- ============================================
-- ROLLBACK
-- ============================================

--ROLLBACK CREATE TABLE country (id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), name VARCHAR(255) NOT NULL, code VARCHAR(10) NOT NULL, phone_code VARCHAR(10) NOT NULL, state BOOLEAN NOT NULL DEFAULT TRUE, created_date TIMESTAMP NOT NULL DEFAULT NOW(), updated_date TIMESTAMP NOT NULL DEFAULT NOW());
--ROLLBACK INSERT INTO country (id, name, code, phone_code, state, created_date, updated_date) SELECT id, name, code, phone_code, state, created_date, updated_date FROM geo_division WHERE code = 'CO' AND level = 0;

-- liquibase formatted sql
-- changeset alter-user-country-table-geo-division:1737050700000-58

-- ============================================
-- MIGRACIÓN: Alterar tabla user_country
--
-- Redirigir FK country_id de country(id) a geo_division(id).
-- La columna se sigue llamando country_id por claridad
-- semántica, pero ahora apunta a geo_division(id)
-- donde el nodo es de tipo COUNTRY.
--
-- Tablas afectadas:
-- 1. user_country (ALTER)
-- ============================================

-- ============================================
-- 1. Eliminar FK antigua
-- La FK fue creada en changelog-v49.sql como:
--   CONSTRAINT fk_user_country_country
-- ============================================

ALTER TABLE user_country DROP CONSTRAINT IF EXISTS fk_user_country_country;

-- ============================================
-- 2. Redirigir a geo_division
-- ============================================

ALTER TABLE user_country ADD CONSTRAINT fk_user_country_geo_division
    FOREIGN KEY (country_id) REFERENCES geo_division(id) ON DELETE RESTRICT;

-- ============================================
-- 3. Comentarios de documentación
-- ============================================

COMMENT ON COLUMN user_country.country_id IS 'FK a geo_division(id) - nodo de tipo COUNTRY. Se mantiene el nombre country_id por claridad semántica';

-- ============================================
-- ROLLBACK
-- ============================================

--ROLLBACK ALTER TABLE user_country DROP CONSTRAINT IF EXISTS fk_user_country_geo_division;
--ROLLBACK ALTER TABLE user_country ADD CONSTRAINT fk_user_country_country FOREIGN KEY (country_id) REFERENCES country(id) ON DELETE RESTRICT;

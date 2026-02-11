-- liquibase formatted sql
-- changeset migrate-colombia-to-geo-division:1737050200000-53

-- ============================================
-- MIGRACIÓN: Migrar Colombia de country a geo_division
--
-- Se copia el registro existente de la tabla country
-- a la nueva tabla geo_division como nodo raíz (level 0).
-- Se preserva el UUID original para no romper FKs existentes
-- en las tablas location y user_country.
--
-- Tablas afectadas:
-- 1. geo_division (INSERT desde country)
-- ============================================

-- ============================================
-- 1. Migrar Colombia preservando su UUID original
-- ============================================

INSERT INTO geo_division (
    id,
    top_id,
    geo_division_type_id,
    name,
    code,
    phone_code,
    level,
    state,
    created_date,
    updated_date
)
SELECT
    c.id,                                                -- UUID original preservado
    NULL,                                                -- Nodo raíz, sin padre
    'a1000000-0000-0000-0000-000000000001',              -- geo_division_type: COUNTRY
    c.name,                                              -- 'Colombia'
    c.code,                                              -- 'CO'
    c.phone_code,                                        -- '+57'
    0,                                                   -- Level 0 = País
    c.state,
    c.created_date,
    c.updated_date
FROM country c
WHERE c.code = 'CO';

-- ============================================
-- ROLLBACK
-- ============================================

--ROLLBACK DELETE FROM geo_division WHERE code = 'CO' AND level = 0;

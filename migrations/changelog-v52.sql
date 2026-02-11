-- liquibase formatted sql
-- changeset create-geo-division-table:1737050100000-52

-- ============================================
-- MIGRACIÓN: Crear tabla geo_division
--
-- Tabla recursiva que contiene toda la jerarquía
-- geográfica, incluyendo los países como nodos raíz.
--
-- La relación jerárquica se establece mediante top_id:
--   - top_id = NULL → nodo raíz (países)
--   - top_id = UUID → nodo hijo
--
-- El tipo de cada nodo se define por geo_division_type_id
-- que es FK a la tabla geo_division_type.
--
-- Tablas afectadas:
-- 1. geo_division (NUEVA)
-- ============================================

-- ============================================
-- 1. Crear tabla geo_division
-- ============================================

CREATE TABLE geo_division (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    top_id UUID,                                    -- NULL = nodo raíz (países)
    geo_division_type_id UUID NOT NULL,             -- FK a geo_division_type
    name VARCHAR(255) NOT NULL,
    code VARCHAR(20),                               -- Código oficial (ISO 3166, DANE, etc.)
    phone_code VARCHAR(10),                         -- Solo para nodos tipo COUNTRY
    level INTEGER NOT NULL DEFAULT 0,               -- 0=country, 1=department, 2=city, 3=commune...
    state BOOLEAN NOT NULL DEFAULT TRUE,
    created_date TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_date TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_geo_division_top
        FOREIGN KEY (top_id) REFERENCES geo_division(id) ON DELETE RESTRICT,
    CONSTRAINT fk_geo_division_type
        FOREIGN KEY (geo_division_type_id) REFERENCES geo_division_type(id) ON DELETE RESTRICT
);

-- ============================================
-- 2. Crear índices
-- ============================================

CREATE INDEX idx_geo_division_top_id ON geo_division(top_id);
CREATE INDEX idx_geo_division_type_id ON geo_division(geo_division_type_id);
CREATE INDEX idx_geo_division_level ON geo_division(level);
CREATE INDEX idx_geo_division_code ON geo_division(code);
CREATE INDEX idx_geo_division_top_type ON geo_division(top_id, geo_division_type_id);

-- ============================================
-- 3. Comentarios de documentación
-- ============================================

COMMENT ON TABLE geo_division IS 'Jerarquía geográfica recursiva. Los países son nodos raíz (top_id = NULL, level = 0)';
COMMENT ON COLUMN geo_division.top_id IS 'Nodo padre. NULL indica nodo raíz (país)';
COMMENT ON COLUMN geo_division.geo_division_type_id IS 'Tipo de división geográfica (FK a geo_division_type)';
COMMENT ON COLUMN geo_division.name IS 'Nombre de la división geográfica';
COMMENT ON COLUMN geo_division.code IS 'Código oficial (ISO 3166 para países, DANE para departamentos/ciudades de Colombia, etc.)';
COMMENT ON COLUMN geo_division.phone_code IS 'Código telefónico. Solo aplica para nodos tipo COUNTRY (+57, +52, etc.)';
COMMENT ON COLUMN geo_division.level IS 'Nivel jerárquico: 0=country, 1=department/state, 2=city, 3=commune/locality, etc.';

-- ============================================
-- ROLLBACK
-- ============================================

--ROLLBACK DROP TABLE IF EXISTS geo_division;

-- liquibase formatted sql
-- changeset alter-location-table-geo-division:1737050600000-57

-- ============================================
-- MIGRACIÓN: Alterar tabla location
--
-- 1. Redirigir FK country_id de country(id) a geo_division(id)
-- 2. Eliminar campo city VARCHAR(100)
-- 3. Agregar campo city_id UUID FK a geo_division(id)
-- 4. Agregar campo latitude DECIMAL(10,8) nullable
-- 5. Agregar campo longitude DECIMAL(11,8) nullable
-- 6. Agregar campo google_place_id VARCHAR(255) nullable
--
-- Tablas afectadas:
-- 1. location (ALTER)
-- ============================================

-- ============================================
-- 1. Redirigir FK country_id a geo_division
-- La FK original fue creada inline como:
--   country_id UUID REFERENCES country (id)
-- PostgreSQL genera el nombre: location_country_id_fkey
-- ============================================

ALTER TABLE location DROP CONSTRAINT IF EXISTS location_country_id_fkey;

ALTER TABLE location ADD CONSTRAINT fk_location_country
    FOREIGN KEY (country_id) REFERENCES geo_division(id) ON DELETE RESTRICT;

-- ============================================
-- 2. Eliminar campo city VARCHAR (no en producción)
-- ============================================

ALTER TABLE location DROP COLUMN city;

-- ============================================
-- 3. Agregar columna city_id (FK a geo_division)
-- ============================================

ALTER TABLE location ADD COLUMN city_id UUID;

ALTER TABLE location ADD CONSTRAINT fk_location_city
    FOREIGN KEY (city_id) REFERENCES geo_division(id) ON DELETE RESTRICT;

CREATE INDEX idx_location_city_id ON location(city_id);

-- ============================================
-- 4. Agregar coordenadas geográficas
-- Nullable para implementación futura.
-- DECIMAL(10,8) para latitud: -90.00000000 a 90.00000000
-- DECIMAL(11,8) para longitud: -180.00000000 a 180.00000000
-- Precisión: ~1.1mm (más que suficiente)
-- ============================================

ALTER TABLE location ADD COLUMN latitude DECIMAL(10, 8);
ALTER TABLE location ADD COLUMN longitude DECIMAL(11, 8);

ALTER TABLE location ADD CONSTRAINT chk_location_latitude
    CHECK (latitude IS NULL OR (latitude >= -90 AND latitude <= 90));

ALTER TABLE location ADD CONSTRAINT chk_location_longitude
    CHECK (longitude IS NULL OR (longitude >= -180 AND longitude <= 180));

-- Índice parcial: solo indexa filas con coordenadas no nulas
CREATE INDEX idx_location_coordinates ON location(latitude, longitude)
    WHERE latitude IS NOT NULL AND longitude IS NOT NULL;

-- ============================================
-- 5. Agregar Google Place ID
-- Nullable, para integración futura con Google Maps Places API.
-- Ejemplo de valor: ChIJd8BlQ2BZwokRAFUEcm_qrcA
-- ============================================

ALTER TABLE location ADD COLUMN google_place_id VARCHAR(255);

-- ============================================
-- 6. Comentarios de documentación
-- ============================================

COMMENT ON COLUMN location.country_id IS 'FK a geo_division(id) - nodo de tipo COUNTRY';
COMMENT ON COLUMN location.city_id IS 'FK a geo_division(id) - nodo de tipo CITY';
COMMENT ON COLUMN location.latitude IS 'Coordenada de latitud (-90 a 90). Nullable para implementación futura';
COMMENT ON COLUMN location.longitude IS 'Coordenada de longitud (-180 a 180). Nullable para implementación futura';
COMMENT ON COLUMN location.google_place_id IS 'Google Maps Place ID. Nullable para integración futura';

-- ============================================
-- ROLLBACK
-- ============================================

--ROLLBACK ALTER TABLE location DROP COLUMN IF EXISTS google_place_id;
--ROLLBACK DROP INDEX IF EXISTS idx_location_coordinates;
--ROLLBACK ALTER TABLE location DROP CONSTRAINT IF EXISTS chk_location_longitude;
--ROLLBACK ALTER TABLE location DROP CONSTRAINT IF EXISTS chk_location_latitude;
--ROLLBACK ALTER TABLE location DROP COLUMN IF EXISTS longitude;
--ROLLBACK ALTER TABLE location DROP COLUMN IF EXISTS latitude;
--ROLLBACK DROP INDEX IF EXISTS idx_location_city_id;
--ROLLBACK ALTER TABLE location DROP CONSTRAINT IF EXISTS fk_location_city;
--ROLLBACK ALTER TABLE location DROP COLUMN IF EXISTS city_id;
--ROLLBACK ALTER TABLE location ADD COLUMN city VARCHAR(100);
--ROLLBACK ALTER TABLE location DROP CONSTRAINT IF EXISTS fk_location_country;
--ROLLBACK ALTER TABLE location ADD CONSTRAINT location_country_id_fkey FOREIGN KEY (country_id) REFERENCES country(id);

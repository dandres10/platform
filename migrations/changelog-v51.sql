-- liquibase formatted sql
-- changeset create-geo-division-type-table:1737050000000-51

-- ============================================
-- MIGRACIÓN: Crear tabla geo_division_type
--
-- Define los tipos de división geográfica de forma
-- dinámica (COUNTRY, DEPARTMENT, CITY, etc.).
-- Reemplaza el uso de enums hardcodeados.
--
-- Tablas afectadas:
-- 1. geo_division_type (NUEVA)
-- ============================================

-- ============================================
-- 1. Crear tabla geo_division_type
-- ============================================

CREATE TABLE geo_division_type (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL UNIQUE,         -- COUNTRY, DEPARTMENT, CITY, etc.
    label VARCHAR(255) NOT NULL,              -- Etiqueta para UI: "País", "Departamento", "Ciudad"
    description TEXT,                         -- Descripción opcional del tipo
    state BOOLEAN NOT NULL DEFAULT TRUE,
    created_date TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_date TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ============================================
-- 2. Comentarios de documentación
-- ============================================

COMMENT ON TABLE geo_division_type IS 'Define los tipos de división geográfica de forma dinámica';
COMMENT ON COLUMN geo_division_type.name IS 'Código único del tipo (COUNTRY, DEPARTMENT, CITY, etc.)';
COMMENT ON COLUMN geo_division_type.label IS 'Etiqueta para mostrar en la UI';
COMMENT ON COLUMN geo_division_type.description IS 'Descripción opcional del tipo de división';

-- ============================================
-- 3. Insertar registros iniciales (12 tipos)
-- ============================================

INSERT INTO geo_division_type (id, name, label, description, state, created_date, updated_date)
VALUES
    -- Nivel 0: País (nodo raíz)
    ('a1000000-0000-0000-0000-000000000001', 'COUNTRY', 'País', 'Nodo raíz, equivale a la antigua tabla country', TRUE, NOW(), NOW()),

    -- Nivel 1: Divisiones de primer nivel (según país)
    ('a1000000-0000-0000-0000-000000000002', 'DEPARTMENT', 'Departamento', 'División de primer nivel (Colombia)', TRUE, NOW(), NOW()),
    ('a1000000-0000-0000-0000-000000000003', 'STATE', 'Estado', 'División de primer nivel (México, USA)', TRUE, NOW(), NOW()),
    ('a1000000-0000-0000-0000-000000000004', 'PROVINCE', 'Provincia', 'División de primer nivel (Argentina, España)', TRUE, NOW(), NOW()),
    ('a1000000-0000-0000-0000-000000000005', 'REGION', 'Región', 'División intermedia', TRUE, NOW(), NOW()),

    -- Nivel 2: Ciudades y municipios
    ('a1000000-0000-0000-0000-000000000006', 'CITY', 'Ciudad', 'Ciudad principal', TRUE, NOW(), NOW()),
    ('a1000000-0000-0000-0000-000000000007', 'MUNICIPALITY', 'Municipio', 'Municipio', TRUE, NOW(), NOW()),

    -- Nivel 3: Subdivisiones de ciudades
    ('a1000000-0000-0000-0000-000000000008', 'COMMUNE', 'Comuna', 'Comuna (Medellín, Cali, etc.)', TRUE, NOW(), NOW()),
    ('a1000000-0000-0000-0000-000000000009', 'LOCALITY', 'Localidad', 'Localidad (Bogotá)', TRUE, NOW(), NOW()),
    ('a1000000-0000-0000-0000-00000000000a', 'NEIGHBORHOOD', 'Barrio', 'Barrio o sector', TRUE, NOW(), NOW()),

    -- Otros
    ('a1000000-0000-0000-0000-00000000000b', 'DISTRICT', 'Distrito', 'Distrito', TRUE, NOW(), NOW()),
    ('a1000000-0000-0000-0000-00000000000c', 'ZONE', 'Zona', 'Zona geográfica', TRUE, NOW(), NOW());

-- ============================================
-- ROLLBACK
-- ============================================

--ROLLBACK DROP TABLE IF EXISTS geo_division_type;

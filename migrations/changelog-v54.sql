-- liquibase formatted sql
-- changeset insert-colombia-departments:1737050300000-54

-- ============================================
-- MIGRACIÓN: Insertar departamentos de Colombia
--
-- 33 departamentos (32 + Bogotá D.C.) con level = 1,
-- tipo DEPARTMENT y top_id apuntando al nodo Colombia.
--
-- Códigos DANE oficiales como campo code.
--
-- Tablas afectadas:
-- 1. geo_division (INSERT 33 registros)
-- ============================================

-- ============================================
-- 1. Insertar 33 departamentos de Colombia
-- ============================================

INSERT INTO geo_division (id, top_id, geo_division_type_id, name, code, phone_code, level, state, created_date, updated_date)
VALUES
    -- Antioquia
    ('b2000000-0000-0000-0000-000000000001',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Antioquia', '05', NULL, 1, TRUE, NOW(), NOW()),

    -- Atlántico
    ('b2000000-0000-0000-0000-000000000002',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Atlántico', '08', NULL, 1, TRUE, NOW(), NOW()),

    -- Bogotá D.C.
    ('b2000000-0000-0000-0000-000000000003',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Bogotá D.C.', '11', NULL, 1, TRUE, NOW(), NOW()),

    -- Bolívar
    ('b2000000-0000-0000-0000-000000000004',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Bolívar', '13', NULL, 1, TRUE, NOW(), NOW()),

    -- Boyacá
    ('b2000000-0000-0000-0000-000000000005',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Boyacá', '15', NULL, 1, TRUE, NOW(), NOW()),

    -- Caldas
    ('b2000000-0000-0000-0000-000000000006',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Caldas', '17', NULL, 1, TRUE, NOW(), NOW()),

    -- Caquetá
    ('b2000000-0000-0000-0000-000000000007',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Caquetá', '18', NULL, 1, TRUE, NOW(), NOW()),

    -- Cauca
    ('b2000000-0000-0000-0000-000000000008',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Cauca', '19', NULL, 1, TRUE, NOW(), NOW()),

    -- Cesar
    ('b2000000-0000-0000-0000-000000000009',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Cesar', '20', NULL, 1, TRUE, NOW(), NOW()),

    -- Córdoba
    ('b2000000-0000-0000-0000-00000000000a',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Córdoba', '23', NULL, 1, TRUE, NOW(), NOW()),

    -- Cundinamarca
    ('b2000000-0000-0000-0000-00000000000b',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Cundinamarca', '25', NULL, 1, TRUE, NOW(), NOW()),

    -- Chocó
    ('b2000000-0000-0000-0000-00000000000c',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Chocó', '27', NULL, 1, TRUE, NOW(), NOW()),

    -- Huila
    ('b2000000-0000-0000-0000-00000000000d',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Huila', '41', NULL, 1, TRUE, NOW(), NOW()),

    -- La Guajira
    ('b2000000-0000-0000-0000-00000000000e',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'La Guajira', '44', NULL, 1, TRUE, NOW(), NOW()),

    -- Magdalena
    ('b2000000-0000-0000-0000-00000000000f',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Magdalena', '47', NULL, 1, TRUE, NOW(), NOW()),

    -- Meta
    ('b2000000-0000-0000-0000-000000000010',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Meta', '50', NULL, 1, TRUE, NOW(), NOW()),

    -- Nariño
    ('b2000000-0000-0000-0000-000000000011',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Nariño', '52', NULL, 1, TRUE, NOW(), NOW()),

    -- Norte de Santander
    ('b2000000-0000-0000-0000-000000000012',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Norte de Santander', '54', NULL, 1, TRUE, NOW(), NOW()),

    -- Quindío
    ('b2000000-0000-0000-0000-000000000013',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Quindío', '63', NULL, 1, TRUE, NOW(), NOW()),

    -- Risaralda
    ('b2000000-0000-0000-0000-000000000014',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Risaralda', '66', NULL, 1, TRUE, NOW(), NOW()),

    -- Santander
    ('b2000000-0000-0000-0000-000000000015',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Santander', '68', NULL, 1, TRUE, NOW(), NOW()),

    -- Sucre
    ('b2000000-0000-0000-0000-000000000016',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Sucre', '70', NULL, 1, TRUE, NOW(), NOW()),

    -- Tolima
    ('b2000000-0000-0000-0000-000000000017',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Tolima', '73', NULL, 1, TRUE, NOW(), NOW()),

    -- Valle del Cauca
    ('b2000000-0000-0000-0000-000000000018',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Valle del Cauca', '76', NULL, 1, TRUE, NOW(), NOW()),

    -- Arauca
    ('b2000000-0000-0000-0000-000000000019',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Arauca', '81', NULL, 1, TRUE, NOW(), NOW()),

    -- Casanare
    ('b2000000-0000-0000-0000-00000000001a',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Casanare', '85', NULL, 1, TRUE, NOW(), NOW()),

    -- Putumayo
    ('b2000000-0000-0000-0000-00000000001b',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Putumayo', '86', NULL, 1, TRUE, NOW(), NOW()),

    -- San Andrés y Providencia
    ('b2000000-0000-0000-0000-00000000001c',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'San Andrés y Providencia', '88', NULL, 1, TRUE, NOW(), NOW()),

    -- Amazonas
    ('b2000000-0000-0000-0000-00000000001d',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Amazonas', '91', NULL, 1, TRUE, NOW(), NOW()),

    -- Guainía
    ('b2000000-0000-0000-0000-00000000001e',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Guainía', '94', NULL, 1, TRUE, NOW(), NOW()),

    -- Guaviare
    ('b2000000-0000-0000-0000-00000000001f',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Guaviare', '95', NULL, 1, TRUE, NOW(), NOW()),

    -- Vaupés
    ('b2000000-0000-0000-0000-000000000020',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Vaupés', '97', NULL, 1, TRUE, NOW(), NOW()),

    -- Vichada
    ('b2000000-0000-0000-0000-000000000021',
     (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0),
     'a1000000-0000-0000-0000-000000000002', 'Vichada', '99', NULL, 1, TRUE, NOW(), NOW());

-- ============================================
-- ROLLBACK
-- ============================================

--ROLLBACK DELETE FROM geo_division WHERE level = 1 AND top_id = (SELECT id FROM geo_division WHERE code = 'CO' AND level = 0);

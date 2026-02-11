-- =====================================================
-- Script Manual: Actualizar city_id en Location
-- =====================================================
-- Fecha: Enero 23, 2026
-- Propósito: Asignar city_id a locations existentes que tienen city_id = NULL
-- 
-- IMPORTANTE: Este script es un EJEMPLO. Debes ajustar los UUIDs y nombres
--             de locations según tus datos reales.
-- =====================================================

-- 1. Primero, consultar las ciudades disponibles en Colombia
-- =====================================================
SELECT 
    gd.id as city_id,
    gd.name as city_name,
    gd.code as city_code,
    gd.level,
    gdt.name as type_name
FROM geo_division gd
INNER JOIN geo_division_type gdt ON gd.geo_division_type_id = gdt.id
WHERE gdt.name = 'CITY' 
  AND gd.state = TRUE
ORDER BY gd.name;

-- 2. Consultar las locations que necesitan city_id
-- =====================================================
SELECT 
    id,
    name,
    address,
    city_id,
    state
FROM location
WHERE city_id IS NULL 
  AND state = TRUE;

-- 3. EJEMPLO: Actualizar locations de Bogotá
-- =====================================================
-- PASO 1: Obtener el UUID de Bogotá ciudad
WITH bogota_city AS (
    SELECT gd.id
    FROM geo_division gd
    INNER JOIN geo_division_type gdt ON gd.geo_division_type_id = gdt.id
    WHERE gd.name = 'Bogotá' 
      AND gdt.name = 'CITY'
      AND gd.level = 2
      AND gd.state = TRUE
    LIMIT 1
)
-- PASO 2: Actualizar locations que están en Bogotá
-- AJUSTAR: Cambiar los nombres de las locations según tus datos reales
UPDATE location
SET city_id = (SELECT id FROM bogota_city)
WHERE name IN ('Chico', 'Suba')  -- ⚠️ AJUSTAR SEGÚN TUS DATOS
  AND city_id IS NULL;

-- 4. EJEMPLO: Actualizar locations de Medellín
-- =====================================================
WITH medellin_city AS (
    SELECT gd.id
    FROM geo_division gd
    INNER JOIN geo_division_type gdt ON gd.geo_division_type_id = gdt.id
    WHERE gd.name = 'Medellín' 
      AND gdt.name = 'CITY'
      AND gd.level = 2
      AND gd.state = TRUE
    LIMIT 1
)
UPDATE location
SET city_id = (SELECT id FROM medellin_city)
WHERE name IN ('Sede Poblado', 'Sede Laureles')  -- ⚠️ AJUSTAR SEGÚN TUS DATOS
  AND city_id IS NULL;

-- 5. EJEMPLO: Actualizar locations de Cali
-- =====================================================
WITH cali_city AS (
    SELECT gd.id
    FROM geo_division gd
    INNER JOIN geo_division_type gdt ON gd.geo_division_type_id = gdt.id
    WHERE gd.name = 'Cali' 
      AND gdt.name = 'CITY'
      AND gd.level = 2
      AND gd.state = TRUE
    LIMIT 1
)
UPDATE location
SET city_id = (SELECT id FROM cali_city)
WHERE name IN ('Sede Centro')  -- ⚠️ AJUSTAR SEGÚN TUS DATOS
  AND city_id IS NULL;

-- 6. Verificar las actualizaciones
-- =====================================================
SELECT 
    l.id,
    l.name as location_name,
    l.address,
    l.city_id,
    gd.name as city_name,
    l.state
FROM location l
LEFT JOIN geo_division gd ON l.city_id = gd.id
ORDER BY l.name;

-- 7. Verificar que no queden locations sin city_id (opcional)
-- =====================================================
-- Este query debe retornar 0 filas si todas las locations activas tienen city_id
SELECT 
    id,
    name,
    address
FROM location
WHERE city_id IS NULL 
  AND state = TRUE;

-- =====================================================
-- NOTAS IMPORTANTES:
-- =====================================================
-- 1. Este script es SAFE - Los UPDATE usan WHERE city_id IS NULL
--    para no sobrescribir valores existentes
--
-- 2. Todos los nombres de ciudades deben coincidir EXACTAMENTE
--    con los nombres en la tabla geo_division
--
-- 3. Si tu location está en una ciudad que no existe en geo_division,
--    primero debes insertar esa ciudad usando el endpoint de GeoDivision
--
-- 4. El campo city_id es OPCIONAL (nullable), así que no es obligatorio
--    asignarlo si prefieres mantenerlo NULL temporalmente
--
-- 5. Para locations de prueba o temporales, puedes dejar city_id en NULL
-- =====================================================

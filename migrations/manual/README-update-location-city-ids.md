# Guía: Actualizar city_id en Locations Existentes

**Fecha**: Enero 23, 2026  
**Relacionado con**: Migración de Divisiones Geográficas (07-13-geographic-division-spec.md)

---

## 🎯 Objetivo

Después de la migración del sistema de divisiones geográficas, las **locations existentes** tienen `city_id = NULL`. Esta guía explica cómo asignar el `city_id` correcto a cada sede.

---

## 📋 Contexto

### ¿Por qué `city_id` está en NULL?

1. Las locations fueron creadas **antes** de la migración cuando solo existía el campo `city` (texto libre)
2. La migración **creó la columna** `city_id` pero no asignó valores automáticamente
3. El campo `city_id` es **opcional (nullable)** para no romper datos existentes

### ¿Qué impacto tiene?

- ✅ **El login funciona correctamente** - Retorna `city_id: null`
- ✅ **No hay errores** - El sistema sigue operando normalmente
- ⚠️ **Información incompleta** - No se puede determinar la ciudad exacta de cada sede
- ⚠️ **Falta de validación** - No se puede verificar que la ciudad pertenezca al país correcto

---

## 🛠️ Solución

### Opción 1: Actualización Manual (SQL) - RECOMENDADO

**Archivo:** `/Users/maleon/Documents/yo/platform/migrations/manual/update-location-city-ids.sql`

#### Paso 1: Consultar ciudades disponibles

```sql
SELECT 
    gd.id as city_id,
    gd.name as city_name,
    gd.code as city_code
FROM geo_division gd
INNER JOIN geo_division_type gdt ON gd.geo_division_type_id = gdt.id
WHERE gdt.name = 'CITY' 
  AND gd.state = TRUE
ORDER BY gd.name;
```

**Resultado esperado:**
```
city_id                              | city_name        | city_code
-------------------------------------|------------------|----------
uuid-1234...                         | Medellín         | 05001
uuid-5678...                         | Bogotá           | 11001
uuid-9012...                         | Cali             | 76001
...
```

#### Paso 2: Identificar locations sin city_id

```sql
SELECT 
    id,
    name,
    address,
    city_id
FROM location
WHERE city_id IS NULL 
  AND state = TRUE;
```

**Resultado esperado:**
```
id                                   | name   | address            | city_id
-------------------------------------|--------|--------------------|--------
8f72c1c5-1783-40f8-bc3c-73f0d017f66e | Chico  | carrera 11 # 100   | NULL
9f72c1c5-1783-40f8-bc3c-73f0d017f66e | Suba   | carrera 11 # 100   | NULL
```

#### Paso 3: Actualizar locations con el city_id correcto

**Ejemplo para Bogotá:**

```sql
-- Obtener el UUID de Bogotá y actualizar locations
WITH bogota_city AS (
    SELECT gd.id
    FROM geo_division gd
    INNER JOIN geo_division_type gdt ON gd.geo_division_type_id = gdt.id
    WHERE gd.name = 'Bogotá' 
      AND gdt.name = 'CITY'
      AND gd.level = 2
    LIMIT 1
)
UPDATE location
SET city_id = (SELECT id FROM bogota_city)
WHERE name IN ('Chico', 'Suba')  -- ⚠️ Ajustar según tus locations
  AND city_id IS NULL;
```

#### Paso 4: Verificar

```sql
SELECT 
    l.name as location_name,
    l.address,
    gd.name as city_name,
    gd.code as city_code
FROM location l
LEFT JOIN geo_division gd ON l.city_id = gd.id
WHERE l.state = TRUE
ORDER BY l.name;
```

**Resultado esperado:**
```
location_name | address            | city_name | city_code
--------------|--------------------|-----------|-----------
Chico         | carrera 11 # 100   | Bogotá    | 11001
Suba          | carrera 11 # 100   | Bogotá    | 11001
```

---

### Opción 2: Actualización vía API (PUT /location)

Puedes usar el endpoint de actualización de Location para asignar el `city_id`:

**Request:**
```http
PUT /location
Content-Type: application/json
Authorization: Bearer <token>

{
  "id": "8f72c1c5-1783-40f8-bc3c-73f0d017f66e",
  "company_id": "1f9a2dd5-2cf6-4350-b3d1-10dc4e8ba730",
  "country_id": "2eaf062f-5281-40dc-be40-4e28e0e8e8cc",
  "city_id": "uuid-de-bogota",  // ← Agregar este campo
  "name": "Chico",
  "address": "carrera 11 # 100",
  "phone": "4562323",
  "email": "info@goluti.com",
  "main_location": true,
  "state": true
}
```

**Ventaja:** Usa la lógica de negocio existente  
**Desventaja:** Requiere hacer una request por cada location

---

## 🔍 Consultas Útiles

### Ver jerarquía de una ciudad

```sql
-- Ver la jerarquía completa: Colombia > Bogotá D.C. > Bogotá
WITH RECURSIVE hierarchy AS (
    -- Nodo inicial (Bogotá ciudad)
    SELECT id, name, top_id, level, 0 as depth
    FROM geo_division
    WHERE name = 'Bogotá' AND level = 2
    
    UNION ALL
    
    -- Padres recursivos
    SELECT gd.id, gd.name, gd.top_id, gd.level, h.depth + 1
    FROM geo_division gd
    INNER JOIN hierarchy h ON gd.id = h.top_id
)
SELECT name, level, depth
FROM hierarchy
ORDER BY depth DESC;
```

**Resultado:**
```
name           | level | depth
---------------|-------|------
Colombia       | 0     | 2
Bogotá D.C.    | 1     | 1
Bogotá         | 2     | 0
```

### Ver todas las ciudades de Colombia

```sql
SELECT 
    gd.name as city_name,
    gd.code as city_code,
    parent.name as department_name
FROM geo_division gd
INNER JOIN geo_division_type gdt ON gd.geo_division_type_id = gdt.id
LEFT JOIN geo_division parent ON gd.top_id = parent.id
WHERE gdt.name = 'CITY' 
  AND gd.state = TRUE
ORDER BY parent.name, gd.name;
```

---

## ✅ Verificación Post-Actualización

Después de actualizar los `city_id`, el login debe retornar:

```json
{
  "location": {
    "id": "8f72c1c5-1783-40f8-bc3c-73f0d017f66e",
    "name": "Chico",
    "address": "carrera 11 # 100",
    "city_id": "uuid-de-bogota",  // ✅ Ya no NULL
    "phone": "4562323",
    "email": "info@goluti.com",
    "main_location": true,
    "latitude": null,
    "longitude": null,
    "google_place_id": null,
    "state": true
  }
}
```

---

## 📝 Notas Importantes

1. **El campo es opcional** - `city_id` puede quedarse en NULL si no conoces la ciudad exacta
2. **Validación de jerarquía** - El `city_id` debe ser un nodo de tipo CITY (level = 2)
3. **Consistencia con country** - La ciudad debe pertenecer al país especificado en `country_id`
4. **Datos de prueba** - Para locations de prueba/staging, puedes dejar `city_id` en NULL temporalmente

---

## 🔗 Referencias

- **Especificación Principal**: `docs/07-flows/07-13-geographic-division-spec.md`
- **Script SQL**: `migrations/manual/update-location-city-ids.sql`
- **Mapper de Login**: `src/infrastructure/database/repositories/business/mappers/auth/login/login_mapper.py`

---

**Fin del Documento**

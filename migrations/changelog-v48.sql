-- liquibase formatted sql
-- changeset user-location-rol-nullable-location:1736790600000-48

-- ============================================
-- 1. Hacer location_id nullable
-- Esto permite registrar usuarios externos sin ubicación
-- ============================================

ALTER TABLE user_location_rol ALTER COLUMN location_id DROP NOT NULL;

-- ============================================
-- 2. Crear índice parcial para usuarios externos
-- Optimiza consultas donde location_id IS NULL
-- ============================================

CREATE INDEX idx_user_location_rol_external 
ON user_location_rol(user_id, rol_id) 
WHERE location_id IS NULL;

-- ============================================
-- 3. Comentario para documentación
-- ============================================

COMMENT ON COLUMN user_location_rol.location_id IS 
'ID de la ubicación. NULL para usuarios externos (rol USER).';

--ROLLBACK DROP INDEX IF EXISTS idx_user_location_rol_external;
--ROLLBACK ALTER TABLE user_location_rol ALTER COLUMN location_id SET NOT NULL;

-- liquibase formatted sql
-- changeset add-menu-type-column:1736704200000-47

-- ============================================
-- 1. Agregar columna type a tabla menu
-- ============================================

ALTER TABLE menu ADD COLUMN type VARCHAR(20) NOT NULL DEFAULT 'INTERNAL';

-- ============================================
-- 2. Actualizar menús existentes
-- El menú "Mis Citas" es EXTERNAL (para usuarios externos)
-- ============================================

UPDATE menu 
SET type = 'EXTERNAL'
WHERE id = 'a0b65172-26d5-4a5c-9c93-6fdfa9a0d46a';

-- ============================================
-- 3. Crear índice para optimizar consultas por type
-- ============================================

CREATE INDEX idx_menu_type ON menu(type);

--ROLLBACK DROP INDEX IF EXISTS idx_menu_type;
--ROLLBACK ALTER TABLE menu DROP COLUMN type;

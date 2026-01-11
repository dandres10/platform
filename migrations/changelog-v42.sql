-- liquibase formatted sql
-- changeset update-menu-servicios-icon:1734750000000-42

-- ============================================
-- Actualizar icono del menú Servicios a bell
-- ============================================

UPDATE menu SET 
    icon = 'bell'
WHERE "name" = 'Servicios';

--ROLLBACK UPDATE menu SET icon = 'briefcase' WHERE "name" = 'Servicios';


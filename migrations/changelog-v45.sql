-- liquibase formatted sql
-- changeset update-menu-citas-icon:1736531400000-45

-- ============================================
-- Actualizar icono del menú Citas
-- Cambiar de 'calendar' a 'clock' para diferenciarlo de Agenda
-- ============================================

UPDATE menu 
SET icon = 'clock', 
    updated_date = NOW()
WHERE label = 'menu.appointments';

--ROLLBACK UPDATE menu SET icon = 'calendar', updated_date = NOW() WHERE label = 'menu.appointments';

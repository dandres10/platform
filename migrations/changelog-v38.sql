-- liquibase formatted sql
-- changeset update-menu-i18n-format:1734220800000-38

-- ============================================
-- Actualizar menús existentes a formato i18n
-- Cambiar label y description a llaves de traducción
-- Estandarizar iconos y rutas
-- ============================================

-- Actualizar Home
UPDATE menu SET 
    "label" = 'menu.home', 
    description = 'menu.home_description',
    icon = 'home',
    route = '/home'
WHERE "name" = 'Home';

-- Actualizar Users
UPDATE menu SET 
    "label" = 'menu.users', 
    description = 'menu.users_description',
    icon = 'users',
    route = '/users'
WHERE "name" = 'Users';

--ROLLBACK UPDATE menu SET "label" = 'Encuentra todo acá', description = 'Home for the application', icon = 'home-icon', route = '/platform/home' WHERE "name" = 'Home' AND company_id IS NULL;
--ROLLBACK UPDATE menu SET "label" = 'users', description = 'users', icon = 'home-icon', route = '/users' WHERE "name" = 'Users' AND company_id IS NULL;

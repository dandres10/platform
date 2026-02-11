-- liquibase formatted sql
-- changeset create-user-country-table:1736877000000-49

-- ============================================
-- 1. Crear tabla user_country
-- Asocia usuarios externos con su país de origen
-- ============================================

CREATE TABLE user_country (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE,
    country_id UUID NOT NULL,
    state BOOLEAN NOT NULL DEFAULT TRUE,
    created_date TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_date TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT fk_user_country_user 
        FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    CONSTRAINT fk_user_country_country 
        FOREIGN KEY (country_id) REFERENCES country(id) ON DELETE RESTRICT
);

-- ============================================
-- 2. Crear índices
-- ============================================

CREATE INDEX idx_user_country_user_id ON user_country(user_id);
CREATE INDEX idx_user_country_country_id ON user_country(country_id);

-- ============================================
-- 3. Comentarios de documentación
-- ============================================

COMMENT ON TABLE user_country IS 'Asocia usuarios externos con su país de origen';
COMMENT ON COLUMN user_country.user_id IS 'ID del usuario (único - un usuario solo tiene un país)';
COMMENT ON COLUMN user_country.country_id IS 'ID del país asociado';

--ROLLBACK DROP TABLE IF EXISTS user_country;

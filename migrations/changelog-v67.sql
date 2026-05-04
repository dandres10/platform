-- liquibase formatted sql
-- changeset spec-004-ddl-drifts:1740585600000-67

-- SPEC-004 T3

--RUN

-- D1: rol UNIQUE compuesto (company_id, code) — eliminar UNIQUE simple si existe
ALTER TABLE rol DROP CONSTRAINT IF EXISTS rol_code_key;
CREATE UNIQUE INDEX IF NOT EXISTS idx_rol_company_code ON rol (company_id, code);

-- D3: api_token.token UNIQUE
CREATE UNIQUE INDEX IF NOT EXISTS idx_api_token_token ON api_token (token);

-- D4: menu.type CHECK IN ('INTERNAL', 'EXTERNAL')
ALTER TABLE menu DROP CONSTRAINT IF EXISTS chk_menu_type;
ALTER TABLE menu ADD CONSTRAINT chk_menu_type
    CHECK (type IN ('INTERNAL', 'EXTERNAL'));

-- D5: location partial unique — solo 1 main_location por company
-- Cleanup pre-constraint: si hay duplicados, mantener la primera (created_date asc, id asc)
UPDATE location SET main_location = FALSE
WHERE id IN (
    SELECT id FROM (
        SELECT id, ROW_NUMBER() OVER (
            PARTITION BY company_id
            ORDER BY created_date, id
        ) as rn
        FROM location
        WHERE main_location = TRUE
    ) t WHERE t.rn > 1
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_location_main_per_company
    ON location (company_id) WHERE main_location = TRUE;

-- D7: user.identification UNIQUE (sin datos legacy duplicados, platform NO en prod)
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_identification ON "user" (identification);

-- D10: user_location_rol partial unique para usuarios externos (location_id IS NULL)
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_location_rol_external_unique
    ON user_location_rol (user_id, rol_id) WHERE location_id IS NULL;

-- D11: rol.code CHECK enum estricto
ALTER TABLE rol DROP CONSTRAINT IF EXISTS chk_rol_code;
ALTER TABLE rol ADD CONSTRAINT chk_rol_code
    CHECK (code IN ('ADMIN', 'COLLA', 'USER'));

-- D12: geo_division.code UNIQUE compuesto (top_id, geo_division_type_id, code)
CREATE UNIQUE INDEX IF NOT EXISTS idx_geo_division_code_unique
    ON geo_division (top_id, geo_division_type_id, code) WHERE code IS NOT NULL;

--FIN RUN

--ROLLBACK
DROP INDEX IF EXISTS idx_geo_division_code_unique;
ALTER TABLE rol DROP CONSTRAINT IF EXISTS chk_rol_code;
DROP INDEX IF EXISTS idx_user_location_rol_external_unique;
DROP INDEX IF EXISTS idx_user_identification;
DROP INDEX IF EXISTS idx_location_main_per_company;
ALTER TABLE menu DROP CONSTRAINT IF EXISTS chk_menu_type;
DROP INDEX IF EXISTS idx_api_token_token;
DROP INDEX IF EXISTS idx_rol_company_code;
--FIN ROLLBACK

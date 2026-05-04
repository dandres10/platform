# SPEC-003 T5
import os
from typing import List, Optional
from sqlalchemy import text
from src.core.config import settings


def _t(table: str) -> str:
    s = settings.database_schema
    return f'{s}."{table}"' if s else f'"{table}"'


# ============================================================================
# Tier S — siempre activas, rápidas (multi-tenant + unicidad + consistencia)
# ============================================================================

async def check_inv_001_main_location_unique(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-001: máximo 1 location con main_location=true por company.
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT company_id, COUNT(*) AS cnt
            FROM {_t('location')}
            WHERE main_location = true AND state = true
              AND company_id = ANY(:company_ids)
            GROUP BY company_id
            HAVING COUNT(*) > 1
            LIMIT 5
        """), {"company_ids": company_ids})
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-001 main_location_unique] {len(rows)} violations: {[(r.company_id, r.cnt) for r in rows]}"


async def check_inv_002_company_currency_one_base(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-002 / SPEC-001 R15: máximo 1 company_currency.is_base=true por company.
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT company_id, COUNT(*) AS cnt
            FROM {_t('company_currency')}
            WHERE is_base = true AND state = true
              AND company_id = ANY(:company_ids)
            GROUP BY company_id
            HAVING COUNT(*) > 1
            LIMIT 5
        """), {"company_ids": company_ids})
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-002 company_currency_one_base] {len(rows)} violations"


async def check_inv_003_currency_location_in_company_currency(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-003 / SPEC-001 PLT-006: currency_location.currency_id ∈ company_currency.
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT cl.id, cl.currency_id, cl.location_id
            FROM {_t('currency_location')} cl
            JOIN {_t('location')} l ON l.id = cl.location_id
            WHERE cl.state = true AND l.company_id = ANY(:company_ids)
              AND NOT EXISTS (
                  SELECT 1 FROM {_t('company_currency')} cc
                  WHERE cc.company_id = l.company_id AND cc.currency_id = cl.currency_id
                    AND cc.state = true
              )
            LIMIT 5
        """), {"company_ids": company_ids})
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-003 currency_location_in_company_currency] {len(rows)} violations"


async def check_inv_004_user_email_unique(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-004: emails únicos en user (multi-tenant en suite).
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT u.email AS email, COUNT(*) AS cnt
            FROM {_t('user')} u
            JOIN {_t('platform')} p ON p.id = u.platform_id
            JOIN {_t('location')} l ON l.id = p.location_id
            WHERE l.company_id = ANY(:company_ids)
            GROUP BY u.email
            HAVING COUNT(*) > 1
            LIMIT 5
        """), {"company_ids": company_ids})
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-004 user_email_unique] {len(rows)} violations"


async def check_inv_005_company_nit_unique(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-005: NIT único en companies de la suite.
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT nit, COUNT(*) AS cnt
            FROM {_t('company')}
            WHERE id = ANY(:company_ids)
            GROUP BY nit
            HAVING COUNT(*) > 1
            LIMIT 5
        """), {"company_ids": company_ids})
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-005 company_nit_unique] {len(rows)} violations"


async def check_inv_006_user_location_rol_consistency(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-006: user_location_rol.location_id apunta a location de la suite.
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT ulr.id
            FROM {_t('user_location_rol')} ulr
            LEFT JOIN {_t('location')} l ON l.id = ulr.location_id
            WHERE ulr.location_id IS NOT NULL AND ulr.state = true
              AND (l.id IS NULL OR NOT (l.company_id = ANY(:company_ids)))
              AND ulr.user_id IN (
                  SELECT u.id FROM {_t('user')} u
                  JOIN {_t('platform')} p ON p.id = u.platform_id
                  JOIN {_t('location')} l2 ON l2.id = p.location_id
                  WHERE l2.company_id = ANY(:company_ids)
              )
            LIMIT 5
        """), {"company_ids": company_ids})
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-006 user_location_rol_consistency] {len(rows)} violations"


async def check_inv_007_api_token_active_unique_per_rol(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-007: máximo 1 api_token activo por rol_id.
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT at.rol_id, COUNT(*) AS cnt
            FROM {_t('api_token')} at
            JOIN {_t('rol')} r ON r.id = at.rol_id
            WHERE at.state = true AND r.company_id = ANY(:company_ids)
            GROUP BY at.rol_id
            HAVING COUNT(*) > 1
            LIMIT 5
        """), {"company_ids": company_ids})
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-007 api_token_unique_per_rol] {len(rows)} violations"


async def check_inv_008_user_identification_unique(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-008 / SPEC-004: user.identification UNIQUE.
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT u.identification, COUNT(*) AS cnt
            FROM {_t('user')} u
            JOIN {_t('platform')} p ON p.id = u.platform_id
            JOIN {_t('location')} l ON l.id = p.location_id
            WHERE l.company_id = ANY(:company_ids)
            GROUP BY u.identification
            HAVING COUNT(*) > 1
            LIMIT 5
        """), {"company_ids": company_ids})
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-008 user_identification_unique] {len(rows)} violations"


async def check_inv_009_user_platform_id_valid(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-009: cada user.platform_id apunta a platform existente.
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT u.id
            FROM {_t('user')} u
            LEFT JOIN {_t('platform')} p ON p.id = u.platform_id
            JOIN {_t('platform')} p2 ON p2.id = u.platform_id
            JOIN {_t('location')} l ON l.id = p2.location_id
            WHERE p.id IS NULL AND l.company_id = ANY(:company_ids)
            LIMIT 5
        """), {"company_ids": company_ids})
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-009 user_platform_id_valid] {len(rows)} violations"


async def check_inv_010_external_user_no_location(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-010: user_location_rol con location_id=NULL debe tener rol externo (USER).
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT ulr.id, r.code
            FROM {_t('user_location_rol')} ulr
            JOIN {_t('rol')} r ON r.id = ulr.rol_id
            WHERE ulr.location_id IS NULL AND ulr.state = true
              AND r.code != 'USER'
            LIMIT 5
        """))
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-010 external_user_no_location] {len(rows)} violations"


async def check_inv_011_user_location_rol_unique(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-011: user_location_rol no duplica (user_id, location_id, rol_id) activo.
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT user_id, location_id, rol_id, COUNT(*) AS cnt
            FROM {_t('user_location_rol')}
            WHERE state = true
            GROUP BY user_id, location_id, rol_id
            HAVING COUNT(*) > 1
            LIMIT 5
        """))
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-011 user_location_rol_unique] {len(rows)} violations"


async def check_inv_012_company_currency_unique_pair(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-012: company_currency no duplica (company_id, currency_id) activo.
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT company_id, currency_id, COUNT(*) AS cnt
            FROM {_t('company_currency')}
            WHERE state = true AND company_id = ANY(:company_ids)
            GROUP BY company_id, currency_id
            HAVING COUNT(*) > 1
            LIMIT 5
        """), {"company_ids": company_ids})
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-012 company_currency_unique_pair] {len(rows)} violations"


async def check_inv_013_currency_location_unique_pair(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-013: currency_location no duplica (location_id, currency_id) activo.
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT cl.location_id, cl.currency_id, COUNT(*) AS cnt
            FROM {_t('currency_location')} cl
            JOIN {_t('location')} l ON l.id = cl.location_id
            WHERE cl.state = true AND l.company_id = ANY(:company_ids)
            GROUP BY cl.location_id, cl.currency_id
            HAVING COUNT(*) > 1
            LIMIT 5
        """), {"company_ids": company_ids})
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-013 currency_location_unique_pair] {len(rows)} violations"


async def check_inv_014_rol_permission_unique_pair(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-014: rol_permission no duplica (rol_id, permission_id) activo.
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT rp.rol_id, rp.permission_id, COUNT(*) AS cnt
            FROM {_t('rol_permission')} rp
            JOIN {_t('rol')} r ON r.id = rp.rol_id
            WHERE rp.state = true AND r.company_id = ANY(:company_ids)
            GROUP BY rp.rol_id, rp.permission_id
            HAVING COUNT(*) > 1
            LIMIT 5
        """), {"company_ids": company_ids})
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-014 rol_permission_unique_pair] {len(rows)} violations"


async def check_inv_015_menu_permission_unique_pair(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-015: menu_permission no duplica (menu_id, permission_id) activo.
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT mp.menu_id, mp.permission_id, COUNT(*) AS cnt
            FROM {_t('menu_permission')} mp
            JOIN {_t('menu')} m ON m.id = mp.menu_id
            WHERE mp.state = true AND m.company_id = ANY(:company_ids)
            GROUP BY mp.menu_id, mp.permission_id
            HAVING COUNT(*) > 1
            LIMIT 5
        """), {"company_ids": company_ids})
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-015 menu_permission_unique_pair] {len(rows)} violations"


async def check_inv_016_api_token_token_unique(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-016 / SPEC-004: api_token.token UNIQUE.
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT at.token, COUNT(*) AS cnt
            FROM {_t('api_token')} at
            JOIN {_t('rol')} r ON r.id = at.rol_id
            WHERE r.company_id = ANY(:company_ids)
            GROUP BY at.token
            HAVING COUNT(*) > 1
            LIMIT 5
        """), {"company_ids": company_ids})
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-016 api_token_token_unique] {len(rows)} violations"


async def check_inv_017_company_has_main_location(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-017: cada company activa tiene al menos 1 location main_location=true activa.
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT c.id, c.nit
            FROM {_t('company')} c
            WHERE c.state = true AND c.id = ANY(:company_ids)
              AND NOT EXISTS (
                  SELECT 1 FROM {_t('location')} l
                  WHERE l.company_id = c.id AND l.main_location = true AND l.state = true
              )
            LIMIT 5
        """), {"company_ids": company_ids})
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-017 company_has_main_location] {len(rows)} companies sin main_location"


async def check_inv_018_company_has_base_currency(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-018 / SPEC-001 R15: cada company activa tiene 1 company_currency.is_base=true.
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT c.id, c.nit
            FROM {_t('company')} c
            WHERE c.state = true AND c.id = ANY(:company_ids)
              AND NOT EXISTS (
                  SELECT 1 FROM {_t('company_currency')} cc
                  WHERE cc.company_id = c.id AND cc.is_base = true AND cc.state = true
              )
            LIMIT 5
        """), {"company_ids": company_ids})
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-018 company_has_base_currency] {len(rows)} companies sin base currency"


async def check_inv_019_location_country_is_country_type(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-019: location.country_id apunta a geo_division con type COUNTRY.
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT l.id, l.country_id, gdt.name AS type_name
            FROM {_t('location')} l
            JOIN {_t('geo_division')} gd ON gd.id = l.country_id
            JOIN {_t('geo_division_type')} gdt ON gdt.id = gd.geo_division_type_id
            WHERE l.country_id IS NOT NULL
              AND l.company_id = ANY(:company_ids)
              AND gdt.name != 'COUNTRY'
            LIMIT 5
        """), {"company_ids": company_ids})
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-019 location_country_is_country_type] {len(rows)} violations"


async def check_inv_020_user_country_user_exists(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-020: cada user_country.user_id existe en user (FK soft).
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT uc.id
            FROM {_t('user_country')} uc
            LEFT JOIN {_t('user')} u ON u.id = uc.user_id
            WHERE u.id IS NULL
            LIMIT 5
        """))
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-020 user_country_user_exists] {len(rows)} orphan user_country"


async def check_inv_021_translation_language_code_valid(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-021: translation.language_code existe en language.code.
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT DISTINCT t.language_code
            FROM {_t('translation')} t
            LEFT JOIN {_t('language')} l ON l.code = t.language_code
            WHERE l.code IS NULL
            LIMIT 5
        """))
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-021 translation_language_code_valid] {len(rows)} unknown codes: {[r.language_code for r in rows]}"


async def check_inv_022_translation_key_lang_unique(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-022 / SPEC-014: translation no duplica (key, language_code, context).
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT key, language_code, context, COUNT(*) AS cnt
            FROM {_t('translation')}
            GROUP BY key, language_code, context
            HAVING COUNT(*) > 1
            LIMIT 5
        """))
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-022 translation_key_lang_unique] {len(rows)} duplicate translations"


# ============================================================================
# Tier A — opt-in (INVARIANTS=1), recursivas / agregaciones costosas
# ============================================================================

async def check_inv_070_geo_division_no_cycles(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-070: jerarquía geo_division sin ciclos.
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            WITH RECURSIVE chain AS (
                SELECT id, top_id, ARRAY[id] AS path, 1 AS depth
                FROM {_t('geo_division')}
                WHERE top_id IS NOT NULL
                UNION ALL
                SELECT c.id, gd.top_id, c.path || gd.id, c.depth + 1
                FROM chain c
                JOIN {_t('geo_division')} gd ON gd.id = c.top_id
                WHERE c.depth < 20 AND NOT (gd.id = ANY(c.path))
            )
            SELECT DISTINCT id FROM chain WHERE depth >= 20 LIMIT 5
        """))
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-070 geo_division_no_cycles] {len(rows)} potential cycles"


async def check_inv_071_geo_division_phone_code_only_country(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-071 / SPEC-004 D6: phone_code solo en COUNTRY.
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT gd.id, gd.name, gdt.name AS type_name
            FROM {_t('geo_division')} gd
            JOIN {_t('geo_division_type')} gdt ON gdt.id = gd.geo_division_type_id
            WHERE gd.phone_code IS NOT NULL AND gdt.name != 'COUNTRY'
            LIMIT 5
        """))
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-071 phone_code_only_country] {len(rows)} violations"


async def check_inv_072_geo_division_level_coherent(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-072: level=0 ⇔ top_id IS NULL.
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT id, name, level, top_id
            FROM {_t('geo_division')}
            WHERE (level = 0 AND top_id IS NOT NULL)
               OR (level > 0 AND top_id IS NULL)
            LIMIT 5
        """))
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-072 geo_division_level_coherent] {len(rows)} violations"


async def check_inv_073_admin_has_role_in_company(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-073: cada user activo dentro de una company tiene al menos 1 user_location_rol activo.
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT u.id, u.email
            FROM {_t('user')} u
            JOIN {_t('platform')} p ON p.id = u.platform_id
            JOIN {_t('location')} l ON l.id = p.location_id
            WHERE u.state = true AND l.company_id = ANY(:company_ids)
              AND NOT EXISTS (
                  SELECT 1 FROM {_t('user_location_rol')} ulr
                  WHERE ulr.user_id = u.id AND ulr.state = true
              )
            LIMIT 5
        """), {"company_ids": company_ids})
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-073 user_has_role] {len(rows)} users sin user_location_rol activo"


async def check_inv_074_company_has_admin(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-074: cada company activa tiene al menos 1 admin activo en su main_location.
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT c.id, c.nit
            FROM {_t('company')} c
            WHERE c.state = true AND c.id = ANY(:company_ids)
              AND NOT EXISTS (
                  SELECT 1 FROM {_t('user_location_rol')} ulr
                  JOIN {_t('rol')} r ON r.id = ulr.rol_id
                  JOIN {_t('location')} l ON l.id = ulr.location_id
                  WHERE l.company_id = c.id AND ulr.state = true AND r.code = 'ADMIN'
              )
            LIMIT 5
        """), {"company_ids": company_ids})
        rows = result.fetchall()
    if not rows:
        return None
    return f"[INV-074 company_has_admin] {len(rows)} companies sin admin"


# ============================================================================
# Tier B — canarios estructurales (INVARIANTS=full), DDL drift detection
# ============================================================================

async def check_inv_080_critical_fk_constraints(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-080 / SPEC-004 T3: FK constraints críticas en DDL.
    expected_fks = [
        ("user", "platform_id"),
        ("user_location_rol", "user_id"),
        ("user_location_rol", "rol_id"),
        ("rol_permission", "rol_id"),
        ("rol_permission", "permission_id"),
        ("menu_permission", "menu_id"),
        ("menu_permission", "permission_id"),
        ("api_token", "rol_id"),
        ("currency_location", "currency_id"),
        ("currency_location", "location_id"),
        ("user_country", "user_id"),
        ("user_country", "country_id"),
    ]
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT tc.table_name, kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = :schema
        """), {"schema": settings.database_schema})
        existing = {(row.table_name, row.column_name) for row in result}
    missing = [fk for fk in expected_fks if fk not in existing]
    if not missing:
        return None
    return f"[INV-080 critical_fk_constraints] {len(missing)} missing: {missing}"


async def check_inv_081_critical_unique_constraints(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-081 / SPEC-004: UNIQUE constraints o UNIQUE indexes críticos en DDL.
    expected_uniques = [
        ("api_token", "token"),
        ("user", "identification"),
    ]
    async with engine.connect() as conn:
        # UNIQUE constraints
        c_result = await conn.execute(text("""
            SELECT tc.table_name, kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'UNIQUE' AND tc.table_schema = :schema
        """), {"schema": settings.database_schema})
        existing = {(row.table_name, row.column_name) for row in c_result}
        # UNIQUE indexes
        i_result = await conn.execute(text("""
            SELECT t.relname AS table_name, a.attname AS column_name
            FROM pg_index ix
            JOIN pg_class i ON i.oid = ix.indexrelid
            JOIN pg_class t ON t.oid = ix.indrelid
            JOIN pg_namespace n ON n.oid = t.relnamespace
            JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
            WHERE ix.indisunique = true AND n.nspname = :schema AND ix.indnatts = 1
        """), {"schema": settings.database_schema})
        existing |= {(row.table_name, row.column_name) for row in i_result}
    missing = [u for u in expected_uniques if u not in existing]
    if not missing:
        return None
    return f"[INV-081 critical_unique_constraints] {len(missing)} missing: {missing}"


async def check_inv_082_critical_check_constraints(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-082 / SPEC-004 T3: CHECK constraints críticas en DDL.
    expected_checks = ["chk_menu_type", "chk_rol_code"]
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT constraint_name FROM information_schema.table_constraints
            WHERE constraint_type = 'CHECK' AND table_schema = :schema
        """), {"schema": settings.database_schema})
        existing = {row.constraint_name for row in result}
    missing = [c for c in expected_checks if c not in existing]
    if not missing:
        return None
    return f"[INV-082 critical_check_constraints] {len(missing)} missing: {missing}"


async def check_inv_083_partial_indexes(engine, company_ids: List[str]) -> Optional[str]:
    # SPEC-003 INV-083 / SPEC-004 T3: partial indexes críticos en DDL.
    expected_indexes = [
        "idx_location_main_per_company",
        "idx_user_location_rol_external_unique",
        "idx_geo_division_code_unique",
        "idx_user_identification",
    ]
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT indexname FROM pg_indexes WHERE schemaname = :schema
        """), {"schema": settings.database_schema})
        existing = {row.indexname for row in result}
    missing = [i for i in expected_indexes if i not in existing]
    if not missing:
        return None
    return f"[INV-083 partial_indexes] {len(missing)} missing: {missing}"


# ============================================================================
# Registro y ejecución
# ============================================================================

TIER_S = [
    check_inv_001_main_location_unique,
    check_inv_002_company_currency_one_base,
    check_inv_003_currency_location_in_company_currency,
    check_inv_004_user_email_unique,
    check_inv_005_company_nit_unique,
    check_inv_006_user_location_rol_consistency,
    check_inv_007_api_token_active_unique_per_rol,
    check_inv_008_user_identification_unique,
    check_inv_009_user_platform_id_valid,
    check_inv_010_external_user_no_location,
    check_inv_011_user_location_rol_unique,
    check_inv_012_company_currency_unique_pair,
    check_inv_013_currency_location_unique_pair,
    check_inv_014_rol_permission_unique_pair,
    check_inv_015_menu_permission_unique_pair,
    check_inv_016_api_token_token_unique,
    check_inv_017_company_has_main_location,
    check_inv_018_company_has_base_currency,
    check_inv_019_location_country_is_country_type,
    check_inv_020_user_country_user_exists,
    check_inv_021_translation_language_code_valid,
    check_inv_022_translation_key_lang_unique,
]

TIER_A = [
    check_inv_070_geo_division_no_cycles,
    check_inv_071_geo_division_phone_code_only_country,
    check_inv_072_geo_division_level_coherent,
    check_inv_073_admin_has_role_in_company,
    check_inv_074_company_has_admin,
]

TIER_B = [
    check_inv_080_critical_fk_constraints,
    check_inv_081_critical_unique_constraints,
    check_inv_082_critical_check_constraints,
    check_inv_083_partial_indexes,
]


async def run_all(engine, company_ids: List[str]) -> List[str]:
    level = os.getenv("INVARIANTS", "default")
    invariants = list(TIER_S)
    if level in ("1", "full"):
        invariants += TIER_A
    if level == "full":
        invariants += TIER_B

    violations = []
    for check in invariants:
        try:
            result = await check(engine, company_ids)
            if result:
                violations.append(result)
        except Exception as e:
            violations.append(f"[{check.__name__}] check raised {type(e).__name__}: {e}")
    return violations

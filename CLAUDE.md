# Goluti Backend Platform - Claude Code Context

## Migrations
- **Format**: SQL puro con Liquibase (`-- liquibase formatted sql`, `-- changeset`)
- **Location**: `migrations/changelog-vNN.sql` (actualmente hasta v59)
- **No usa Alembic** - no hay archivos Python de migracion
- **Sin prefijo de schema** en SQL (solo `menu`, no `platform.menu`)
- **Rollback**: `--ROLLBACK SQL_STATEMENT` en comentarios
- **Logica procedural**: Usar `DO $$ ... END $$` para loops

## UUID Handling
- Entities de BD usan `server_default=text('uuid_generate_v4()')`
- Modelos Pydantic usan `UUID4` pero data semilla tiene UUIDs no-v4 (ej: `a1000000-...`)
- Para campos que referencian tablas semilla, usar `UUID` de stdlib en vez de `UUID4`
- Ya corregido: modelos `geo_division`, modelos `location` (city_id)

## Config Dependency Patterns (`src/core/methods/get_config.py`)
- `get_config` - Autenticado (Bearer token + language header)
- `get_config_login` - Solo login (language + DB session, sin auth)
- `get_config_public` - Endpoints publicos (language + DB session, sin auth)

## Enums Clave
- `MENU_TYPE`: INTERNAL, EXTERNAL (`src/core/enums/menu_type.py`)
- `ROL_TYPE`: ADMIN, COLLA, USER (`src/core/enums/rol_type.py`)

## Sistema de Menus
- Menus template: `company_id = NULL`
- Se clonan por compania via `CloneMenusForCompanyUseCase` (algoritmo de 2 pases)
- Cadena de permisos: `rol -> rol_permission -> permission -> menu_permission -> menu`
- Solo menus `INTERNAL` se clonan; `EXTERNAL` son globales
- Spec de migracion: `docs/07-flows/07-15-menu-parent-migration-spec.md`

## Patron de Entities
- Base import: `from src.core.models.base import Base`
- Columnas usan `server_default=text(...)` no `default=...`
- Schema via `__table_args__ = {"schema": settings.database_schema}`

## Agentes Disponibles (`~/.claude/agents/` o `.claude/agents/`)
- **Platform**: backend-developer, code-reviewer, database-expert
- **Appointment**: backend-developer, code-reviewer, database-expert
- **Goluti**: code-reviewer, frontend-developer
- **Pixelon**: component-reviewer, design-system-developer

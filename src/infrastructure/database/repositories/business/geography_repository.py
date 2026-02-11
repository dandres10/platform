
from pydantic import UUID4
from typing import List, Optional, Tuple, Union
from src.core.config import settings
from sqlalchemy.future import select
from sqlalchemy import func
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.infrastructure.database.entities.geo_division_entity import GeoDivisionEntity
from src.infrastructure.database.entities.geo_division_type_entity import GeoDivisionTypeEntity


class GeographyRepository:

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def get_countries(
        self, config: Config
    ) -> Optional[List[Tuple[GeoDivisionEntity, GeoDivisionTypeEntity]]]:
        """Obtiene todos los países (level = 0, nodos raíz)."""
        async with config.async_db as db:
            stmt = (
                select(GeoDivisionEntity, GeoDivisionTypeEntity)
                .join(
                    GeoDivisionTypeEntity,
                    GeoDivisionEntity.geo_division_type_id == GeoDivisionTypeEntity.id,
                )
                .filter(GeoDivisionEntity.level == 0)
                .filter(GeoDivisionEntity.top_id.is_(None))
                .filter(GeoDivisionEntity.state == True)
                .order_by(GeoDivisionEntity.name)
            )
            result = await db.execute(stmt)
            rows = result.all()
            return rows if rows else None

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def get_types_by_country(
        self, config: Config, country_id: UUID4
    ) -> Optional[List]:
        """Obtiene los tipos de división disponibles para un país con conteo."""
        async with config.async_db as db:
            from sqlalchemy import text as sa_text
            
            schema = settings.database_schema
            raw_sql = sa_text(f"""
                WITH RECURSIVE descendants AS (
                    SELECT id, geo_division_type_id, level
                    FROM {schema}.geo_division
                    WHERE top_id = :country_id AND state = TRUE
                    
                    UNION ALL
                    
                    SELECT gd.id, gd.geo_division_type_id, gd.level
                    FROM {schema}.geo_division gd
                    INNER JOIN descendants d ON gd.top_id = d.id
                    WHERE gd.state = TRUE
                )
                SELECT 
                    gdt.id,
                    gdt.name,
                    gdt.label,
                    d.level,
                    COUNT(d.id) as count
                FROM descendants d
                INNER JOIN {schema}.geo_division_type gdt ON d.geo_division_type_id = gdt.id
                WHERE gdt.state = TRUE
                GROUP BY gdt.id, gdt.name, gdt.label, d.level
                ORDER BY d.level
            """)
            
            result = await db.execute(raw_sql, {"country_id": str(country_id)})
            rows = result.all()
            return rows if rows else None

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def get_by_country_and_type(
        self, config: Config, country_id: UUID4, type_name: str
    ) -> Optional[List[Tuple[GeoDivisionEntity, GeoDivisionTypeEntity]]]:
        """Obtiene divisiones de un país filtradas por tipo."""
        async with config.async_db as db:
            from sqlalchemy import text as sa_text

            schema = settings.database_schema
            raw_sql = sa_text(f"""
                WITH RECURSIVE descendants AS (
                    SELECT id, top_id, geo_division_type_id, name, code, phone_code, level, state, created_date, updated_date
                    FROM {schema}.geo_division
                    WHERE top_id = :country_id AND state = TRUE
                    
                    UNION ALL
                    
                    SELECT gd.id, gd.top_id, gd.geo_division_type_id, gd.name, gd.code, gd.phone_code, gd.level, gd.state, gd.created_date, gd.updated_date
                    FROM {schema}.geo_division gd
                    INNER JOIN descendants d ON gd.top_id = d.id
                    WHERE gd.state = TRUE
                )
                SELECT 
                    d.id, d.top_id, d.geo_division_type_id, d.name, d.code, d.phone_code, d.level, d.state, d.created_date, d.updated_date,
                    gdt.id as type_id, gdt.name as type_name, gdt.label as type_label, gdt.description as type_description, gdt.state as type_state, gdt.created_date as type_created_date, gdt.updated_date as type_updated_date
                FROM descendants d
                INNER JOIN {schema}.geo_division_type gdt ON d.geo_division_type_id = gdt.id
                WHERE gdt.name = :type_name AND gdt.state = TRUE
                ORDER BY d.name
            """)
            
            result = await db.execute(raw_sql, {"country_id": str(country_id), "type_name": type_name})
            rows = result.all()
            
            if not rows:
                return None
            
            mapped = []
            for row in rows:
                geo_entity = GeoDivisionEntity()
                geo_entity.id = row.id
                geo_entity.top_id = row.top_id
                geo_entity.geo_division_type_id = row.geo_division_type_id
                geo_entity.name = row.name
                geo_entity.code = row.code
                geo_entity.phone_code = row.phone_code
                geo_entity.level = row.level
                geo_entity.state = row.state
                
                type_entity = GeoDivisionTypeEntity()
                type_entity.id = row.type_id
                type_entity.name = row.type_name
                type_entity.label = row.type_label
                type_entity.description = row.type_description
                type_entity.state = row.type_state
                
                mapped.append((geo_entity, type_entity))
            
            return mapped

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def get_children(
        self, config: Config, parent_id: UUID4
    ) -> Optional[List[Tuple[GeoDivisionEntity, GeoDivisionTypeEntity]]]:
        """Obtiene hijos directos de una división."""
        async with config.async_db as db:
            stmt = (
                select(GeoDivisionEntity, GeoDivisionTypeEntity)
                .join(
                    GeoDivisionTypeEntity,
                    GeoDivisionEntity.geo_division_type_id == GeoDivisionTypeEntity.id,
                )
                .filter(GeoDivisionEntity.top_id == parent_id)
                .filter(GeoDivisionEntity.state == True)
                .order_by(GeoDivisionEntity.name)
            )
            result = await db.execute(stmt)
            rows = result.all()
            return rows if rows else None

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def get_children_by_type(
        self, config: Config, parent_id: UUID4, type_name: str
    ) -> Optional[List[Tuple[GeoDivisionEntity, GeoDivisionTypeEntity]]]:
        """Obtiene hijos directos de una división filtrados por tipo."""
        async with config.async_db as db:
            stmt = (
                select(GeoDivisionEntity, GeoDivisionTypeEntity)
                .join(
                    GeoDivisionTypeEntity,
                    GeoDivisionEntity.geo_division_type_id == GeoDivisionTypeEntity.id,
                )
                .filter(GeoDivisionEntity.top_id == parent_id)
                .filter(GeoDivisionTypeEntity.name == type_name)
                .filter(GeoDivisionEntity.state == True)
                .filter(GeoDivisionTypeEntity.state == True)
                .order_by(GeoDivisionEntity.name)
            )
            result = await db.execute(stmt)
            rows = result.all()
            return rows if rows else None

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def get_hierarchy(
        self, config: Config, node_id: UUID4
    ) -> Optional[List[Tuple[GeoDivisionEntity, GeoDivisionTypeEntity]]]:
        """Obtiene la jerarquía completa hacia arriba (nodo hasta raíz)."""
        async with config.async_db as db:
            from sqlalchemy import text as sa_text

            schema = settings.database_schema
            raw_sql = sa_text(f"""
                WITH RECURSIVE ancestors AS (
                    SELECT id, top_id, geo_division_type_id, name, code, phone_code, level, state, created_date, updated_date, 0 as depth
                    FROM {schema}.geo_division
                    WHERE id = :node_id AND state = TRUE
                    
                    UNION ALL
                    
                    SELECT gd.id, gd.top_id, gd.geo_division_type_id, gd.name, gd.code, gd.phone_code, gd.level, gd.state, gd.created_date, gd.updated_date, a.depth + 1
                    FROM {schema}.geo_division gd
                    INNER JOIN ancestors a ON gd.id = a.top_id
                    WHERE gd.state = TRUE
                )
                SELECT 
                    a.id, a.top_id, a.geo_division_type_id, a.name, a.code, a.phone_code, a.level, a.state, a.created_date, a.updated_date, a.depth,
                    gdt.id as type_id, gdt.name as type_name, gdt.label as type_label, gdt.description as type_description, gdt.state as type_state
                FROM ancestors a
                INNER JOIN {schema}.geo_division_type gdt ON a.geo_division_type_id = gdt.id
                ORDER BY a.depth ASC
            """)
            
            result = await db.execute(raw_sql, {"node_id": str(node_id)})
            rows = result.all()
            
            if not rows:
                return None
            
            mapped = []
            for row in rows:
                geo_entity = GeoDivisionEntity()
                geo_entity.id = row.id
                geo_entity.top_id = row.top_id
                geo_entity.geo_division_type_id = row.geo_division_type_id
                geo_entity.name = row.name
                geo_entity.code = row.code
                geo_entity.phone_code = row.phone_code
                geo_entity.level = row.level
                geo_entity.state = row.state
                
                type_entity = GeoDivisionTypeEntity()
                type_entity.id = row.type_id
                type_entity.name = row.type_name
                type_entity.label = row.type_label
                type_entity.description = row.type_description
                type_entity.state = row.type_state
                
                mapped.append((geo_entity, type_entity))
            
            return mapped

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def get_detail(
        self, config: Config, node_id: UUID4
    ) -> Optional[Tuple[GeoDivisionEntity, GeoDivisionTypeEntity]]:
        """Obtiene el detalle de una división específica."""
        async with config.async_db as db:
            stmt = (
                select(GeoDivisionEntity, GeoDivisionTypeEntity)
                .join(
                    GeoDivisionTypeEntity,
                    GeoDivisionEntity.geo_division_type_id == GeoDivisionTypeEntity.id,
                )
                .filter(GeoDivisionEntity.id == node_id)
                .filter(GeoDivisionEntity.state == True)
            )
            result = await db.execute(stmt)
            row = result.first()
            return row if row else None

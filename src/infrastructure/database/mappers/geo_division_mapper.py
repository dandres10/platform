
from typing import List
from src.domain.models.entities.geo_division.index import (
    GeoDivision,
    GeoDivisionSave,
    GeoDivisionUpdate,
)
from src.infrastructure.database.entities.geo_division_entity import GeoDivisionEntity


def map_to_geo_division(entity: GeoDivisionEntity) -> GeoDivision:
    return GeoDivision(
        id=entity.id,
        top_id=entity.top_id,
        geo_division_type_id=entity.geo_division_type_id,
        name=entity.name,
        code=entity.code,
        phone_code=entity.phone_code,
        level=entity.level,
        state=entity.state,
        created_date=entity.created_date,
        updated_date=entity.updated_date,
    )

def map_to_list_geo_division(entities: List[GeoDivisionEntity]) -> List[GeoDivision]:
    return [map_to_geo_division(entity) for entity in entities]

def map_to_geo_division_entity(geo_division: GeoDivision) -> GeoDivisionEntity:
    return GeoDivisionEntity(
        id=geo_division.id,
        top_id=geo_division.top_id,
        geo_division_type_id=geo_division.geo_division_type_id,
        name=geo_division.name,
        code=geo_division.code,
        phone_code=geo_division.phone_code,
        level=geo_division.level,
        state=geo_division.state,
        created_date=geo_division.created_date,
        updated_date=geo_division.updated_date,
    )

def map_to_list_geo_division_entity(items: List[GeoDivision]) -> List[GeoDivisionEntity]:
    return [map_to_geo_division_entity(item) for item in items]

def map_to_save_geo_division_entity(geo_division: GeoDivisionSave) -> GeoDivisionEntity:
    return GeoDivisionEntity(
        top_id=geo_division.top_id,
        geo_division_type_id=geo_division.geo_division_type_id,
        name=geo_division.name,
        code=geo_division.code,
        phone_code=geo_division.phone_code,
        level=geo_division.level,
        state=geo_division.state,
    )

def map_to_update_geo_division_entity(geo_division: GeoDivisionUpdate) -> GeoDivisionEntity:
    return GeoDivisionEntity(
        id=geo_division.id,
        top_id=geo_division.top_id,
        geo_division_type_id=geo_division.geo_division_type_id,
        name=geo_division.name,
        code=geo_division.code,
        phone_code=geo_division.phone_code,
        level=geo_division.level,
        state=geo_division.state,
    )

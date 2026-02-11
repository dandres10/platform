
from typing import List
from src.domain.models.entities.geo_division_type.index import (
    GeoDivisionType,
    GeoDivisionTypeSave,
    GeoDivisionTypeUpdate,
)
from src.infrastructure.database.entities.geo_division_type_entity import GeoDivisionTypeEntity


def map_to_geo_division_type(entity: GeoDivisionTypeEntity) -> GeoDivisionType:
    return GeoDivisionType(
        id=entity.id,
        name=entity.name,
        label=entity.label,
        description=entity.description,
        state=entity.state,
        created_date=entity.created_date,
        updated_date=entity.updated_date,
    )

def map_to_list_geo_division_type(entities: List[GeoDivisionTypeEntity]) -> List[GeoDivisionType]:
    return [map_to_geo_division_type(entity) for entity in entities]

def map_to_geo_division_type_entity(geo_division_type: GeoDivisionType) -> GeoDivisionTypeEntity:
    return GeoDivisionTypeEntity(
        id=geo_division_type.id,
        name=geo_division_type.name,
        label=geo_division_type.label,
        description=geo_division_type.description,
        state=geo_division_type.state,
        created_date=geo_division_type.created_date,
        updated_date=geo_division_type.updated_date,
    )

def map_to_list_geo_division_type_entity(items: List[GeoDivisionType]) -> List[GeoDivisionTypeEntity]:
    return [map_to_geo_division_type_entity(item) for item in items]

def map_to_save_geo_division_type_entity(geo_division_type: GeoDivisionTypeSave) -> GeoDivisionTypeEntity:
    return GeoDivisionTypeEntity(
        name=geo_division_type.name,
        label=geo_division_type.label,
        description=geo_division_type.description,
        state=geo_division_type.state,
    )

def map_to_update_geo_division_type_entity(geo_division_type: GeoDivisionTypeUpdate) -> GeoDivisionTypeEntity:
    return GeoDivisionTypeEntity(
        id=geo_division_type.id,
        name=geo_division_type.name,
        label=geo_division_type.label,
        description=geo_division_type.description,
        state=geo_division_type.state,
    )

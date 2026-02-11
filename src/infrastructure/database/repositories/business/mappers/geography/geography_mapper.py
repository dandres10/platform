
from typing import List
from src.domain.models.business.geography.index import (
    GeoDivisionItemResponse,
    GeoDivisionTypeByCountryResponse,
    GeoDivisionHierarchyItemResponse,
)
from src.infrastructure.database.entities.geo_division_entity import GeoDivisionEntity
from src.infrastructure.database.entities.geo_division_type_entity import GeoDivisionTypeEntity


def map_to_geo_division_item_response(
    entity: GeoDivisionEntity,
    type_entity: GeoDivisionTypeEntity,
) -> GeoDivisionItemResponse:
    return GeoDivisionItemResponse(
        id=entity.id,
        name=entity.name,
        code=entity.code,
        phone_code=entity.phone_code,
        level=entity.level,
        type=type_entity.name,
        type_label=type_entity.label,
    )


def map_to_list_geo_division_item_response(
    rows: list,
) -> List[GeoDivisionItemResponse]:
    """Maps a list of (GeoDivisionEntity, GeoDivisionTypeEntity) tuples to response models."""
    return [
        map_to_geo_division_item_response(entity=row[0], type_entity=row[1])
        for row in rows
    ]


def map_to_geo_division_type_by_country_response(
    type_entity: GeoDivisionTypeEntity,
    level: int,
    count: int,
) -> GeoDivisionTypeByCountryResponse:
    return GeoDivisionTypeByCountryResponse(
        id=type_entity.id,
        name=type_entity.name,
        label=type_entity.label,
        level=level,
        count=count,
    )


def map_to_hierarchy_item_response(
    entity: GeoDivisionEntity,
    type_entity: GeoDivisionTypeEntity,
) -> GeoDivisionHierarchyItemResponse:
    return GeoDivisionHierarchyItemResponse(
        id=entity.id,
        name=entity.name,
        code=entity.code,
        phone_code=entity.phone_code,
        level=entity.level,
        type=type_entity.name,
        type_label=type_entity.label,
    )


from typing import List
from src.domain.models.entities.location.index import (
    Location,
    LocationSave,
    LocationUpdate,
)
from src.infrastructure.database.entities.location_entity import LocationEntity


def map_to_location(location_entity: LocationEntity) -> Location:
    return Location(
        id=location_entity.id,
        company_id=location_entity.company_id,
        country_id=location_entity.country_id,
        name=location_entity.name,
        address=location_entity.address,
        city=location_entity.city,
        phone=location_entity.phone,
        email=location_entity.email,
        main_location=location_entity.main_location,
        state=location_entity.state,
        created_date=location_entity.created_date,
        updated_date=location_entity.updated_date,
    )

def map_to_list_location(location_entities: List[LocationEntity]) -> List[Location]:
    return [map_to_location(location) for location in location_entities]

def map_to_location_entity(location: Location) -> LocationEntity:
    return LocationEntity(
        id=location.id,
        company_id=location.company_id,
        country_id=location.country_id,
        name=location.name,
        address=location.address,
        city=location.city,
        phone=location.phone,
        email=location.email,
        main_location=location.main_location,
        state=location.state,
        created_date=location.created_date,
        updated_date=location.updated_date,
    )

def map_to_list_location_entity(locations: List[Location]) -> List[LocationEntity]:
    return [map_to_location_entity(location) for location in locations]

def map_to_save_location_entity(location: LocationSave) -> LocationEntity:
    return LocationEntity(
        company_id=location.company_id,
        country_id=location.country_id,
        name=location.name,
        address=location.address,
        city=location.city,
        phone=location.phone,
        email=location.email,
        main_location=location.main_location,
        state=location.state,
    )

def map_to_update_location_entity(location: LocationUpdate) -> LocationEntity:
    return LocationEntity(
        id=location.id,
        company_id=location.company_id,
        country_id=location.country_id,
        name=location.name,
        address=location.address,
        city=location.city,
        phone=location.phone,
        email=location.email,
        main_location=location.main_location,
        state=location.state,
    )


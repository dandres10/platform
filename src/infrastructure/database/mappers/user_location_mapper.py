
from typing import List
from src.domain.models.entities.user_location.index import (
    UserLocation,
    UserLocationSave,
    UserLocationUpdate,
)
from src.infrastructure.database.entities.user_location_entity import UserLocationEntity


def map_to_user_location(user_location_entity: UserLocationEntity) -> UserLocation:
    return UserLocation(
        id=userlocation_entity.id,
        user_id=userlocation_entity.user_id,
        location_id=userlocation_entity.location_id,
        state=userlocation_entity.state,
        created_date=userlocation_entity.created_date,
        updated_date=userlocation_entity.updated_date,
    )

def map_to_list_user_location(user_location_entities: List[UserLocationEntity]) -> List[UserLocation]:
    return [map_to_user_location(user_location) for user_location in user_location_entities]

def map_to_user_location_entity(user_location: UserLocation) -> UserLocationEntity:
    return UserLocationEntity(
        id=userlocation.id,
        user_id=userlocation.user_id,
        location_id=userlocation.location_id,
        state=userlocation.state,
        created_date=userlocation.created_date,
        updated_date=userlocation.updated_date,
    )

def map_to_list_user_location_entity(user_locations: List[UserLocation]) -> List[UserLocationEntity]:
    return [map_to_user_location_entity(user_location) for user_location in user_locations]

def map_to_save_user_location_entity(user_location: UserLocationSave) -> UserLocationEntity:
    return UserLocationEntity(
        user_id=user_location.user_id,
        location_id=user_location.location_id,
        state=user_location.state,
    )

def map_to_update_user_location_entity(user_location: UserLocationUpdate) -> UserLocationEntity:
    return UserLocationEntity(
        id=user_location.id,
        user_id=user_location.user_id,
        location_id=user_location.location_id,
        state=user_location.state,
    )


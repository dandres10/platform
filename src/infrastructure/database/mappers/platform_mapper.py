
from typing import List
from src.domain.models.entities.platform.index import (
    Platform,
    PlatformSave,
    PlatformUpdate,
)
from src.infrastructure.database.entities.platform_entity import PlatformEntity


def map_to_platform(platform_entity: PlatformEntity) -> Platform:
    return Platform(
        id=platform_entity.id,
        language_id=platform_entity.language_id,
        location_id=platform_entity.location_id,
        currency_id=platform_entity.currency_id,
        token_expiration_minutes=platform_entity.token_expiration_minutes,
        refresh_token_expiration_minutes=platform_entity.refresh_token_expiration_minutes,
        created_date=platform_entity.created_date,
        updated_date=platform_entity.updated_date,
    )

def map_to_list_platform(platform_entities: List[PlatformEntity]) -> List[Platform]:
    return [map_to_platform(platform) for platform in platform_entities]

def map_to_platform_entity(platform: Platform) -> PlatformEntity:
    return PlatformEntity(
        id=platform.id,
        language_id=platform.language_id,
        location_id=platform.location_id,
        currency_id=platform.currency_id,
        token_expiration_minutes=platform.token_expiration_minutes,
        refresh_token_expiration_minutes=platform.refresh_token_expiration_minutes,
        created_date=platform.created_date,
        updated_date=platform.updated_date,
    )

def map_to_list_platform_entity(platforms: List[Platform]) -> List[PlatformEntity]:
    return [map_to_platform_entity(platform) for platform in platforms]

def map_to_save_platform_entity(platform: PlatformSave) -> PlatformEntity:
    return PlatformEntity(
        language_id=platform.language_id,
        location_id=platform.location_id,
        currency_id=platform.currency_id,
        token_expiration_minutes=platform.token_expiration_minutes,
        refresh_token_expiration_minutes=platform.refresh_token_expiration_minutes,
    )

def map_to_update_platform_entity(platform: PlatformUpdate) -> PlatformEntity:
    return PlatformEntity(
        id=platform.id,
        language_id=platform.language_id,
        location_id=platform.location_id,
        currency_id=platform.currency_id,
        token_expiration_minutes=platform.token_expiration_minutes,
        refresh_token_expiration_minutes=platform.refresh_token_expiration_minutes,
    )


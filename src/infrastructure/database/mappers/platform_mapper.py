from typing import List
from src.domain.models.entities.platform.platform import Platform
from src.infrastructure.database.entities.platform_entity import PlatformEntity


def map_to_platform(platform_entity: PlatformEntity) -> Platform:
    return Platform(
        id=platform_entity.id,
        language=platform_entity.language,
        created_date=platform_entity.created_date,
        updated_date=platform_entity.updated_date,
    )


def map_to_list_platform(platform_entities: List[PlatformEntity]) -> List[Platform]:
    return [map_to_platform(platform) for platform in platform_entities]


def map_to_platform_entity(task: Platform) -> PlatformEntity:
    return PlatformEntity(
        id=task.id,
        language=task.language,
        created_date=task.created_date,
        updated_date=task.updated_date,
    )


def map_to_list_platform_entity(platforms: List[Platform]) -> List[PlatformEntity]:
    return [map_to_platform_entity(platform) for platform in platforms]

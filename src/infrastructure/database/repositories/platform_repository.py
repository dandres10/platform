from typing import Union

from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.domain.models.entities.platform.platform import Platform
from src.domain.services.repositories.entities.i_platform_repository import (
    IPlatformRepository,
)
from src.infrastructure.database.entities.platform_entity import PlatformEntity
from src.infrastructure.database.mappers.platform_mapper import map_to_platform
from src.core.wrappers.execute_transaction import execute_transaction
from src.core.config import settings


class PlatformRepository(IPlatformRepository):

    def save(self, config: Config, params: PlatformEntity) -> Union[Platform, None]:
        db = config.db
        db.add(params)
        db.commit()
        db.refresh(params)
        return map_to_platform(params)


if settings.has_track:
    PlatformRepository.save = execute_transaction(LAYER.I_D_R.value)(
        PlatformRepository.save
    )

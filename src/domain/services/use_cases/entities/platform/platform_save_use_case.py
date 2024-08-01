from typing import Union
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.platform.platform import Platform
from src.domain.models.entities.platform.platform_save import PlatformSave
from src.domain.services.repositories.entities.i_platform_repository import (
    IPlatformRepository,
)
from src.infrastructure.database.entities.platform_entity import PlatformEntity
from src.core.config import settings


class PlatformSaveUseCase:
    def __init__(self, platform_repository: IPlatformRepository):
        self.platform_repository = platform_repository

    def execute(
        self,
        config: Config,
        params: PlatformSave,
    ) -> Union[Platform, str, None]:
        platform = PlatformEntity(language=params.language)
        result = self.platform_repository.save(config=config, params=platform)
        if not result:
            return "Error en el flujo, contactar al administrador"
        return result


if settings.has_track:
    PlatformSaveUseCase.execute = execute_transaction(LAYER.D_S_U_E.value)(
        PlatformSaveUseCase.execute
    )

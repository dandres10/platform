from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.response import Response
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.platform.platform_save import PlatformSave
from src.domain.services.use_cases.entities.platform.platform_save_use_case import (
    PlatformSaveUseCase,
)
from src.infrastructure.database.repositories.platform_repository import (
    PlatformRepository,
)
from src.core.config import settings

platform_repository = PlatformRepository()


class PlatformController:
    def __init__(self) -> None:
        self.platform_save_use_case = PlatformSaveUseCase(platform_repository)

    def save(self, config: Config, params: PlatformSave) -> Response:
        result_save = self.platform_save_use_case.execute(config, params)
        if isinstance(result_save, str):
            return Response.error(None, result_save)
        return Response.success_temporary_message(
            response=result_save, message="Información guarda con exito"
        )
    

if settings.has_track:
    PlatformController.save = execute_transaction(LAYER.I_W_C_E.value)(
        PlatformController.save
    )

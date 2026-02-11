
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.response import Response
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.geo_division.index import (
    GeoDivisionDelete,
    GeoDivisionRead,
    GeoDivisionSave,
    GeoDivisionUpdate,
)
from src.domain.services.use_cases.entities.geo_division.index import (
    GeoDivisionDeleteUseCase,
    GeoDivisionListUseCase,
    GeoDivisionReadUseCase,
    GeoDivisionSaveUseCase,
    GeoDivisionUpdateUseCase,
)
from src.infrastructure.database.repositories.entities.geo_division_repository import (
    GeoDivisionRepository,
)



geo_division_repository = GeoDivisionRepository()


class GeoDivisionController:
    def __init__(self) -> None:
        self.geo_division_save_use_case = GeoDivisionSaveUseCase(geo_division_repository)
        self.geo_division_update_use_case = GeoDivisionUpdateUseCase(geo_division_repository)
        self.geo_division_list_use_case = GeoDivisionListUseCase(geo_division_repository)
        self.geo_division_delete_use_case = GeoDivisionDeleteUseCase(geo_division_repository)
        self.geo_division_read_use_case = GeoDivisionReadUseCase(geo_division_repository)
        self.message = Message()

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def save(self, config: Config, params: GeoDivisionSave) -> Response:
        result_save = await self.geo_division_save_use_case.execute(config=config, params=params)
        if isinstance(result_save, str):
            return Response.error(None, result_save)
        return Response.success_temporary_message(
            response=result_save,
            message= await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_SAVED_INFORMATION.value
                ),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def update(self, config: Config, params: GeoDivisionUpdate) -> Response:
        result_update = await self.geo_division_update_use_case.execute(config=config, params=params)
        if isinstance(result_update, str):
            return Response.error(None, result_update)
        return Response.success_temporary_message(
            response=result_update,
            message= await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_UPDATED_INFORMATION.value
                ),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def list(self, config: Config, params: Pagination) -> Response:
        result_list = await self.geo_division_list_use_case.execute(config=config, params=params)
        if isinstance(result_list, str):
            return Response.error(None, result_list)
        return Response.success_temporary_message(
            response=result_list,
            message= await self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=KEYS_MESSAGES.CORE_QUERY_MADE.value),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def delete(self, config: Config, params: GeoDivisionDelete) -> Response:
        result_delete = await self.geo_division_delete_use_case.execute(config=config, params=params)
        if isinstance(result_delete, str):
            return Response.error(None, result_delete)
        return Response.success_temporary_message(
            response=result_delete,
            message= await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_DELETION_PERFORMED.value
                ),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def read(self, config: Config, params: GeoDivisionRead) -> Response:
        result_read = await self.geo_division_read_use_case.execute(config=config, params=params)
        if isinstance(result_read, str):
            return Response.error(None, result_read)
        return Response.success_temporary_message(
            response=result_read,
            message= await self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=KEYS_MESSAGES.CORE_QUERY_MADE.value),
            ),
        )

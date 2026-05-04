
from typing import Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.enums.keys_errors import KEYS_ERRORS
from src.core.exceptions import BusinessException
from src.core.models.config import Config
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.geo_division.index import GeoDivision, GeoDivisionSave
from src.domain.models.entities.geo_division_type.index import GeoDivisionTypeRead
from src.domain.services.repositories.entities.i_geo_division_repository import (
    IGeoDivisionRepository,
)
from src.domain.services.use_cases.entities.geo_division_type.geo_division_type_read_use_case import (
    GeoDivisionTypeReadUseCase,
)


class GeoDivisionSaveUseCase:
    # SPEC-004 D6
    def __init__(
        self,
        geo_division_repository: IGeoDivisionRepository,
        geo_division_type_read_use_case: GeoDivisionTypeReadUseCase,
    ):
        self.geo_division_repository = geo_division_repository
        self.geo_division_type_read_use_case = geo_division_type_read_use_case
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: GeoDivisionSave,
    ) -> Union[GeoDivision, str, None]:
        # SPEC-004 D6
        if params.phone_code is not None and params.geo_division_type_id is not None:
            type_result = await self.geo_division_type_read_use_case.execute(
                config=config,
                params=GeoDivisionTypeRead(id=params.geo_division_type_id),
            )
            if isinstance(type_result, str) or type_result is None or type_result.name != "COUNTRY":
                raise BusinessException(
                    KEYS_MESSAGES.PLT_GEO_PHONE_CODE_ONLY_COUNTRY.value,
                    KEYS_ERRORS.PLT_GEO_PHONE_CODE_ONLY_COUNTRY.value,
                )

        result = await self.geo_division_repository.save(config=config, params=params)
        if not result:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_ERROR_SAVING_RECORD.value
                ),
            )

        if config.response_type == RESPONSE_TYPE.OBJECT.value:
            return result
        elif config.response_type == RESPONSE_TYPE.DICT.value:
            return result.dict()

        return result

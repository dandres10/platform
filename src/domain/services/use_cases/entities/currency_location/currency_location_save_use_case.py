
from typing import Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.keys_errors import KEYS_ERRORS
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.exceptions import BusinessException
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.currency_location.index import CurrencyLocation, CurrencyLocationSave
from src.domain.services.repositories.entities.i_currency_location_repository import (
    ICurrencyLocationRepository,
)
from src.domain.services.use_cases.entities.company_currency.list_company_currency_use_case import (
    ListCompanyCurrencyUseCase,
)


class CurrencyLocationSaveUseCase:
    # SPEC-001 T6
    def __init__(
        self,
        currency_location_repository: ICurrencyLocationRepository,
        list_company_currency_use_case: ListCompanyCurrencyUseCase,
    ):
        self.currency_location_repository = currency_location_repository
        self.list_company_currency_use_case = list_company_currency_use_case
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: CurrencyLocationSave,
    ) -> Union[CurrencyLocation, str, None]:
        allowed_rows = await self.list_company_currency_use_case.execute(
            config=config,
            params=Pagination(all_data=True),
        )
        allowed_currency_ids = (
            {row.currency_id for row in allowed_rows}
            if isinstance(allowed_rows, list)
            else set()
        )
        if params.currency_id not in allowed_currency_ids:
            raise BusinessException(
                KEYS_MESSAGES.PLT_CURRENCY_NOT_ALLOWED_FOR_COMPANY.value,
                KEYS_ERRORS.PLT_CURRENCY_NOT_ALLOWED_FOR_COMPANY.value,
            )

        result = await self.currency_location_repository.save(config=config, params=params)
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
            return result.model_dump() 

        return result

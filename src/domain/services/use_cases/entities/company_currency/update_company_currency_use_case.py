
from typing import Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.exceptions import BusinessException
from src.core.wrappers.execute_transaction import execute_transaction
from src.core.enums.keys_errors import KEYS_ERRORS
from src.domain.models.entities.company_currency.index import (
    CompanyCurrency,
    CompanyCurrencyRead,
    CompanyCurrencyUpdate,
)
from src.domain.services.repositories.entities.i_company_currency_repository import (
    ICompanyCurrencyRepository,
)


class UpdateCompanyCurrencyUseCase:
    # SPEC-001 T4
    def __init__(self, company_currency_repository: ICompanyCurrencyRepository):
        self.company_currency_repository = company_currency_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: CompanyCurrencyUpdate,
    ) -> Union[CompanyCurrency, str, None]:
        existing = await self.company_currency_repository.read(
            config=config,
            params=CompanyCurrencyRead(id=params.id),
        )
        if not existing:
            raise BusinessException(
                KEYS_MESSAGES.PLT_COMPANY_CURRENCY_NOT_FOUND.value,
                KEYS_ERRORS.PLT_COMPANY_CURRENCY_NOT_FOUND.value,
            )

        if params.is_base is True and not existing.is_base:
            current_base = await self.company_currency_repository.find_base_by_company(
                config=config,
                company_id=existing.company_id,
            )
            if current_base is not None and current_base.id != params.id:
                await self.company_currency_repository.update(
                    config=config,
                    params=CompanyCurrencyUpdate(
                        id=current_base.id,
                        is_base=False,
                    ),
                )

        result = await self.company_currency_repository.update(
            config=config, params=params
        )
        if not result:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=KEYS_MESSAGES.CORE_UPDATE_FAILED.value),
            )

        if config.response_type == RESPONSE_TYPE.OBJECT.value:
            return result
        elif config.response_type == RESPONSE_TYPE.DICT.value:
            return result.dict()

        return result

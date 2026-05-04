
from typing import Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.exceptions import BusinessException
from src.core.wrappers.execute_transaction import execute_transaction
from src.core.enums.keys_errors import KEYS_ERRORS
from src.domain.models.entities.company_currency.index import (
    CompanyCurrency,
    CompanyCurrencyDelete,
    CompanyCurrencyRead,
)
from src.domain.services.repositories.entities.i_company_currency_repository import (
    ICompanyCurrencyRepository,
)


class DeleteCompanyCurrencyUseCase:
    # SPEC-001 T4
    def __init__(self, company_currency_repository: ICompanyCurrencyRepository):
        self.company_currency_repository = company_currency_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: CompanyCurrencyDelete,
    ) -> Union[CompanyCurrency, str, None]:
        target = await self.company_currency_repository.read(
            config=config,
            params=CompanyCurrencyRead(id=params.id),
        )
        if not target:
            raise BusinessException(
                KEYS_MESSAGES.PLT_COMPANY_CURRENCY_NOT_FOUND.value,
                KEYS_ERRORS.PLT_COMPANY_CURRENCY_NOT_FOUND.value,
            )

        if target.is_base:
            current_base = await self.company_currency_repository.find_base_by_company(
                config=config,
                company_id=target.company_id,
            )
            if current_base is not None and current_base.id == target.id:
                all_rows = await self.company_currency_repository.list(
                    config=config,
                    params=Pagination(all_data=True),
                )
                all_rows = all_rows or []
                has_alternative = any(row.id != target.id for row in all_rows)
                if not has_alternative:
                    raise BusinessException(
                        KEYS_MESSAGES.PLT_COMPANY_CURRENCY_BASE_REQUIRED.value,
                        KEYS_ERRORS.PLT_COMPANY_CURRENCY_BASE_REQUIRED.value,
                    )

        result = await self.company_currency_repository.delete(
            config=config, params=params
        )
        if not result:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_RECORD_NOT_FOUND_TO_DELETE.value
                ),
            )

        if config.response_type == RESPONSE_TYPE.OBJECT.value:
            return result
        elif config.response_type == RESPONSE_TYPE.DICT.value:
            return result.model_dump()

        return result

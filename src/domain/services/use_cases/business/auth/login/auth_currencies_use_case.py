from typing import List, Union
from src.core.enums.condition_type import CONDITION_TYPE
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.message import MessageCoreEntity
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.login.auth_currencies_by_location import (
    AuthCurremciesByLocation,
)
from src.domain.models.business.auth.login.auth_login_response import (
    CurrencyLoginResponse,
)
from src.domain.services.use_cases.entities.currency.currency_list_use_case import (
    CurrencyListUseCase,
)
from src.core.config import settings
from src.infrastructure.database.mappers.currency_mapper import map_to_list_currency
from src.infrastructure.database.repositories.business.auth_repository import (
    AuthRepository,
)
from src.infrastructure.database.repositories.business.mappers.auth.login.login_mapper import (
    map_to_currecy_login_response,
)
from src.core.classes.async_message import Message


class AuthCurrenciesUseCase:
    def __init__(
        self,
    ):
        self.auth_repository = AuthRepository()
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(self, config: Config, params: AuthCurremciesByLocation) -> Union[
        List[CurrencyLoginResponse],
        str,
    ]:
        config.response_type = RESPONSE_TYPE.OBJECT
        currencies: List[CurrencyLoginResponse] = []

        results = await self.auth_repository.currencies_by_location(
            config=config, params=params
        )

        if not results:
            print("no se encontraron idiomas")
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_RECORD_NOT_FOUND_TO_DELETE.value
                ),
            )

        for result in results:
            currency_location, currency, location = result
            currencies.append(map_to_currecy_login_response(currency_entity=currency))

        return currencies

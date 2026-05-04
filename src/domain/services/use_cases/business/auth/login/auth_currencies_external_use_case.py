from typing import List, Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.login.auth_login_response import CurrencyLoginResponse
from src.infrastructure.database.repositories.business.auth_repository import AuthRepository


class AuthCurrenciesExternalUseCase:
    """
    Obtiene todas las currencies disponibles para usuarios externos.
    
    A diferencia de los internos que obtienen currencies por location,
    los externos obtienen todas las currencies activas del sistema.
    """
    
    def __init__(self):
        self.auth_repository = AuthRepository()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
    ) -> Union[List[CurrencyLoginResponse], str]:
        config.response_type = RESPONSE_TYPE.OBJECT

        result = await self.auth_repository.all_currencies(config=config)

        if not result:
            return []  # Retornar lista vacía, no error

        return result

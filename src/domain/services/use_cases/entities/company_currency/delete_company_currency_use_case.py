
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
    """Elimina una company_currency con guard de base (R7).

    Si la fila a eliminar es la única `is_base=true` y NO existe otra fila
    para esa company que pueda asumir el rol de base (es decir, no hay
    alternativa), rechazar. Para reasignar la base, el cliente debe primero
    `update` otra fila a `is_base=true` (swap atómico) y luego eliminar la
    antigua.
    """

    def __init__(self, company_currency_repository: ICompanyCurrencyRepository):
        self.company_currency_repository = company_currency_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: CompanyCurrencyDelete,
    ) -> Union[CompanyCurrency, str, None]:
        # Validar existencia + multi-tenant primero.
        target = await self.company_currency_repository.read(
            config=config,
            params=CompanyCurrencyRead(id=params.id),
        )
        if not target:
            raise BusinessException(
                KEYS_MESSAGES.PLT_COMPANY_CURRENCY_NOT_FOUND.value,
                KEYS_ERRORS.PLT_COMPANY_CURRENCY_NOT_FOUND.value,
            )

        # R7: si la fila objetivo es base, verificar que existe alguna otra
        # fila para esa company (si no, eliminar dejaría a la company sin
        # base — prohibido).
        if target.is_base:
            current_base = await self.company_currency_repository.find_base_by_company(
                config=config,
                company_id=target.company_id,
            )
            # Si la base actual es la que se va a eliminar, contar otras filas.
            if current_base is not None and current_base.id == target.id:
                all_rows = await self.company_currency_repository.list(
                    config=config,
                    params=Pagination(all_data=True),
                )
                all_rows = all_rows or []
                # Sin alternativa = solo existe esta fila base, no hay otra
                # candidata para asumir el rol después del delete.
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
            return result.dict()

        return result

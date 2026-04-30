
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
    CompanyCurrencySave,
)
from src.domain.services.repositories.entities.i_company_currency_repository import (
    ICompanyCurrencyRepository,
)
from src.infrastructure.database.mappers.company_currency_mapper import (
    map_to_save_company_currency_entity,
)


class SaveCompanyCurrencyUseCase:
    """Crea una asociación currency ↔ company.

    Reglas de negocio (SPEC-001):
    - R14: la PRIMERA fila para una company debe tener `is_base=true`.
    - R5: si ya hay base y `is_base=true` → rechazar (para promover, usar
      update con swap atómico).
    - R4: combinación `(company_id, currency_id)` duplicada → rechazar antes
      del INSERT con mensaje claro. El UNIQUE constraint del DB es la
      defensa-en-profundidad final.
    """

    def __init__(self, company_currency_repository: ICompanyCurrencyRepository):
        self.company_currency_repository = company_currency_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: CompanyCurrencySave,
    ) -> Union[CompanyCurrency, str, None]:
        company_id = params.company_id

        # Listar filas existentes para la company actual (multi-tenant ya lo
        # aplica el repo). Lo usamos para 3 chequeos: ¿hay alguna?, ¿duplicado?,
        # ¿hay base ya?
        existing_rows = await self.company_currency_repository.list(
            config=config,
            params=Pagination(all_data=True),
        )
        existing_rows = existing_rows or []

        # R4: duplicado (company_id, currency_id).
        if params.currency_id is not None:
            for row in existing_rows:
                if row.currency_id == params.currency_id:
                    raise BusinessException(
                        KEYS_MESSAGES.PLT_COMPANY_CURRENCY_DUPLICATE.value,
                        KEYS_ERRORS.PLT_COMPANY_CURRENCY_DUPLICATE.value,
                    )

        # R5: si ya hay base y el cliente pide is_base=true → rechazar.
        existing_base = await self.company_currency_repository.find_base_by_company(
            config=config,
            company_id=company_id,
        )
        if existing_base is not None and params.is_base:
            raise BusinessException(
                KEYS_MESSAGES.PLT_COMPANY_CURRENCY_BASE_ALREADY_EXISTS.value,
                KEYS_ERRORS.PLT_COMPANY_CURRENCY_BASE_ALREADY_EXISTS.value,
            )

        # R14: si NO hay filas previas y is_base=false → rechazar.
        if not existing_rows and not params.is_base:
            raise BusinessException(
                KEYS_MESSAGES.PLT_COMPANY_CURRENCY_FIRST_MUST_BE_BASE.value,
                KEYS_ERRORS.PLT_COMPANY_CURRENCY_FIRST_MUST_BE_BASE.value,
            )

        entity = map_to_save_company_currency_entity(params)
        result = await self.company_currency_repository.save(config=config, params=entity)
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

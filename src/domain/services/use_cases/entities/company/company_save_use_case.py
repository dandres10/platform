
from typing import Union
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.company.index import Company, CompanySave
from src.domain.services.repositories.entities.i_company_repository import (
    ICompanyRepository,
)
from src.core.config import settings
from src.infrastructure.database.mappers.company_mapper import (
    map_to_save_company_entity,
)
from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity

class CompanySaveUseCase:
    def __init__(self, company_repository: ICompanyRepository):
        self.company_repository = company_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    def execute(
        self,
        config: Config,
        params: CompanySave,
    ) -> Union[Company, str, None]:
        result = map_to_save_company_entity(params)
        result = self.company_repository.save(config=config, params=result)
        if not result:
            return self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_ERROR_SAVING_RECORD.value
                ),
            )
        result = result.dict()
        return result
        
from typing import Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity

from src.domain.models.entities.company.index import CompanyUpdate
from src.domain.services.use_cases.entities.company.company_update_use_case import (
    CompanyUpdateUseCase
)
from src.infrastructure.database.repositories.entities.company_repository import (
    CompanyRepository
)


company_repository = CompanyRepository()


class SoftDeleteCompanyUseCase:
    """
    Inactiva una compañía (soft delete) actualizando state=False.
    Se usa cuando la compañía tiene relaciones activas y no puede ser eliminada físicamente.
    La compañía será eliminada permanentemente después de 1 mes.
    """
    
    def __init__(self):
        self.company_update_uc = CompanyUpdateUseCase(company_repository)
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        company
    ) -> Union[str, bool]:
        """
        Inactiva la compañía actualizando state=False.
        
        Args:
            config: Configuración de la petición
            company: Objeto compañía a inactivar
            
        Returns:
            Union[str, bool]: True si éxito, str con mensaje de error si falla
        """
        update_params = CompanyUpdate(
            id=company.id,
            name=company.name,
            nit=company.nit,
            inactivity_time=company.inactivity_time,
            state=False  # Inactivar compañía
        )
        
        result = await self.company_update_uc.execute(
            config=config,
            params=update_params
        )
        
        if isinstance(result, str):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.DELETE_COMPANY_ERROR_SOFT_DELETE.value
                ),
            )
        
        return True


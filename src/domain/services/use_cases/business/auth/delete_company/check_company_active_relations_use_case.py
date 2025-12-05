from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction


class CheckCompanyActiveRelationsUseCase:
    """
    Verifica si una compañía tiene relaciones activas que impidan su eliminación física.
    Extensible: agregar verificaciones de otras tablas aquí (órdenes, transacciones, etc.)
    """
    
    def __init__(self):
        # Inicializar use cases de otras entidades para verificar relaciones
        # Ejemplo:
        # self.order_list_uc = OrderListUseCase(order_repository)
        # self.transaction_list_uc = TransactionListUseCase(transaction_repository)
        pass

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        company_id: UUID4
    ) -> bool:
        """
        Verifica si la compañía tiene relaciones activas.
        
        Args:
            config: Configuración de la petición
            company_id: ID de la compañía a verificar
            
        Returns:
            bool: True si tiene relaciones activas, False si puede ser eliminada
        """
        # Extensible: agregar verificaciones de otras tablas aquí
        # Ejemplo:
        # orders = await self.order_list_uc.execute(
        #     config=config,
        #     params=Pagination(
        #         filters=[
        #             FilterManager(
        #                 field="company_id",
        #                 condition=CONDITION_TYPE.EQUALS,
        #                 value=str(company_id)
        #             )
        #         ]
        #     )
        # )
        # if orders and not isinstance(orders, str) and len(orders) > 0:
        #     return True
        
        return False


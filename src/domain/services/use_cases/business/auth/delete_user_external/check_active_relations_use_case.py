from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction


class CheckActiveRelationsExternalUseCase:
    """
    Verifica si un usuario externo tiene relaciones activas que impidan su eliminación física.
    Extensible: agregar verificaciones de otras tablas aquí (órdenes, transacciones, etc.)
    """
    
    def __init__(self):
        # Inicializar use cases de otras entidades para verificar relaciones
        # Ejemplo:
        # self.order_list_uc = OrderListUseCase(order_repository)
        pass

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        user_id: UUID4
    ) -> bool:
        """
        Verifica si el usuario externo tiene relaciones activas.
        
        Args:
            config: Configuración de la petición
            user_id: ID del usuario a verificar
            
        Returns:
            bool: True si tiene relaciones activas, False si puede ser eliminado
        """
        # Extensible: agregar verificaciones de otras tablas aquí
        # Por ahora retorna False (sin relaciones adicionales)
        return False


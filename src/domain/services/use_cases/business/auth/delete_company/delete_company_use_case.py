from typing import Union
from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination, FilterManager
from src.core.enums.condition_type import CONDITION_TYPE
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.wrappers.execute_transaction import execute_transaction
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity

from src.domain.models.business.auth.delete_company import (
    DeleteCompanyRequest
)
from src.domain.models.entities.company.index import CompanyRead, CompanyDelete
from src.domain.models.entities.location.index import LocationRead, LocationDelete
from src.domain.models.entities.menu.index import MenuDelete
from src.domain.models.entities.menu_permission.index import MenuPermissionDelete
from src.domain.models.entities.user.index import UserDelete
from src.domain.models.entities.user_location_rol.index import UserLocationRolDelete
from src.domain.models.entities.platform.index import PlatformDelete

from src.domain.services.use_cases.entities.company.company_read_use_case import (
    CompanyReadUseCase
)
from src.domain.services.use_cases.entities.company.company_delete_use_case import (
    CompanyDeleteUseCase
)
from src.domain.services.use_cases.entities.location.location_read_use_case import (
    LocationReadUseCase
)
from src.domain.services.use_cases.entities.location.location_list_use_case import (
    LocationListUseCase
)
from src.domain.services.use_cases.entities.location.location_delete_use_case import (
    LocationDeleteUseCase
)
from src.domain.services.use_cases.entities.menu.menu_list_use_case import (
    MenuListUseCase
)
from src.domain.services.use_cases.entities.menu.menu_delete_use_case import (
    MenuDeleteUseCase
)
from src.domain.services.use_cases.entities.menu_permission.menu_permission_list_use_case import (
    MenuPermissionListUseCase
)
from src.domain.services.use_cases.entities.menu_permission.menu_permission_delete_use_case import (
    MenuPermissionDeleteUseCase
)
from src.domain.services.use_cases.entities.user.user_read_use_case import (
    UserReadUseCase
)
from src.domain.services.use_cases.entities.user.user_delete_use_case import (
    UserDeleteUseCase
)
from src.domain.services.use_cases.entities.user_location_rol.user_location_rol_list_use_case import (
    UserLocationRolListUseCase
)
from src.domain.services.use_cases.entities.user_location_rol.user_location_rol_delete_use_case import (
    UserLocationRolDeleteUseCase
)
from src.domain.services.use_cases.entities.platform.platform_delete_use_case import (
    PlatformDeleteUseCase
)

from .check_company_active_relations_use_case import CheckCompanyActiveRelationsUseCase
from .soft_delete_company_use_case import SoftDeleteCompanyUseCase

from src.infrastructure.database.repositories.entities.company_repository import (
    CompanyRepository
)
from src.infrastructure.database.repositories.entities.location_repository import (
    LocationRepository
)
from src.infrastructure.database.repositories.entities.menu_repository import (
    MenuRepository
)
from src.infrastructure.database.repositories.entities.menu_permission_repository import (
    MenuPermissionRepository
)
from src.infrastructure.database.repositories.entities.user_repository import (
    UserRepository
)
from src.infrastructure.database.repositories.entities.user_location_rol_repository import (
    UserLocationRolRepository
)
from src.infrastructure.database.repositories.entities.platform_repository import (
    PlatformRepository
)


company_repository = CompanyRepository()
location_repository = LocationRepository()
menu_repository = MenuRepository()
menu_permission_repository = MenuPermissionRepository()
user_repository = UserRepository()
user_location_rol_repository = UserLocationRolRepository()
platform_repository = PlatformRepository()


class DeleteCompanyUseCase:
    """
    Use Case para eliminar una compañía del sistema.
    
    Proceso:
    1. Validar que la compañía existe
    2. Validar que el admin pertenece a la compañía
    3. Verificar relaciones activas
    4. Si no tiene relaciones activas: hard delete
    5. Si tiene relaciones activas o falla hard delete: soft delete
    """
    
    def __init__(self):
        # Use cases de lectura
        self.company_read_uc = CompanyReadUseCase(company_repository)
        self.location_read_uc = LocationReadUseCase(location_repository)
        self.location_list_uc = LocationListUseCase(location_repository)
        self.menu_list_uc = MenuListUseCase(menu_repository)
        self.menu_permission_list_uc = MenuPermissionListUseCase(menu_permission_repository)
        self.user_read_uc = UserReadUseCase(user_repository)
        self.user_location_rol_list_uc = UserLocationRolListUseCase(user_location_rol_repository)
        
        # Use cases de eliminación
        self.company_delete_uc = CompanyDeleteUseCase(company_repository)
        self.location_delete_uc = LocationDeleteUseCase(location_repository)
        self.menu_delete_uc = MenuDeleteUseCase(menu_repository)
        self.menu_permission_delete_uc = MenuPermissionDeleteUseCase(menu_permission_repository)
        self.user_delete_uc = UserDeleteUseCase(user_repository)
        self.user_location_rol_delete_uc = UserLocationRolDeleteUseCase(user_location_rol_repository)
        self.platform_delete_uc = PlatformDeleteUseCase(platform_repository)
        
        # Use cases auxiliares
        self.check_active_relations_uc = CheckCompanyActiveRelationsUseCase()
        self.soft_delete_company_uc = SoftDeleteCompanyUseCase()
        
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: DeleteCompanyRequest,
    ) -> Union[str, None]:
        """
        Ejecuta el flujo de eliminación de compañía.
        
        Args:
            config: Configuración de la petición
            params: Datos de la compañía a eliminar
            
        Returns:
            None si eliminación exitosa (hard delete)
            str con mensaje de error o soft delete
        """
        config.response_type = RESPONSE_TYPE.OBJECT

        # 1. Validar que la compañía existe
        company = await self.company_read_uc.execute(
            config=config,
            params=CompanyRead(id=params.company_id)
        )
        if isinstance(company, str) or not company:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.DELETE_COMPANY_NOT_FOUND.value,
                    params={"company_id": str(params.company_id)}
                ),
            )

        # 2. Validar que el admin pertenece a la compañía
        admin_location_id = config.token.location_id
        
        admin_location = await self.location_read_uc.execute(
            config=config,
            params=LocationRead(id=admin_location_id)
        )
        
        if isinstance(admin_location, str) or not admin_location:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.DELETE_COMPANY_UNAUTHORIZED.value
                ),
            )
        
        if str(admin_location.company_id) != str(params.company_id):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.DELETE_COMPANY_UNAUTHORIZED.value
                ),
            )

        # 3. Verificar relaciones activas
        has_active_relations = await self.check_active_relations_uc.execute(
            config=config,
            company_id=params.company_id
        )
        if has_active_relations:
            return await self._handle_soft_delete(config=config, company=company)

        # 4. Intentar hard delete
        try:
            await self._execute_hard_delete(
                config=config,
                company_id=params.company_id
            )
            return None  # Hard delete exitoso
            
        except Exception:
            # Si falla el hard delete, hacer soft delete
            return await self._handle_soft_delete(config=config, company=company)

    async def _execute_hard_delete(
        self,
        config: Config,
        company_id: UUID4
    ) -> None:
        """Ejecuta la eliminación física de la compañía y sus registros relacionados."""
        
        # 4a.1 Obtener todas las locations de la compañía
        locations = await self.location_list_uc.execute(
            config=config,
            params=Pagination(
                filters=[
                    FilterManager(
                        field="company_id",
                        condition=CONDITION_TYPE.EQUALS,
                        value=str(company_id)
                    )
                ],
                all_data=True
            )
        )
        
        if locations and not isinstance(locations, str):
            # 4a.2 Para cada location, eliminar users y sus relaciones
            for location in locations:
                # Obtener user_location_rols de esta location
                user_location_rols = await self.user_location_rol_list_uc.execute(
                    config=config,
                    params=Pagination(
                        filters=[
                            FilterManager(
                                field="location_id",
                                condition=CONDITION_TYPE.EQUALS,
                                value=str(location.id)
                            )
                        ],
                        all_data=True
                    )
                )
                
                if user_location_rols and not isinstance(user_location_rols, str):
                    # Obtener usuarios únicos para eliminar
                    user_ids_to_delete = set()
                    
                    for ulr in user_location_rols:
                        user_ids_to_delete.add(str(ulr.user_id))
                        
                        # Eliminar user_location_rol
                        delete_result = await self.user_location_rol_delete_uc.execute(
                            config=config,
                            params=UserLocationRolDelete(id=ulr.id)
                        )
                        if isinstance(delete_result, str):
                            raise Exception("Error deleting user_location_rol")
                    
                    # Eliminar usuarios y sus platforms
                    for user_id in user_ids_to_delete:
                        # Obtener usuario para conseguir platform_id
                        user = await self.user_read_uc.execute(
                            config=config,
                            params={"id": user_id}
                        )
                        
                        if user and not isinstance(user, str):
                            platform_id = user.platform_id
                            
                            # Eliminar user
                            user_deleted = await self.user_delete_uc.execute(
                                config=config,
                                params=UserDelete(id=user_id)
                            )
                            if isinstance(user_deleted, str):
                                raise Exception("Error deleting user")
                            
                            # Eliminar platform
                            if platform_id:
                                platform_deleted = await self.platform_delete_uc.execute(
                                    config=config,
                                    params=PlatformDelete(id=platform_id)
                                )
                                if isinstance(platform_deleted, str):
                                    raise Exception("Error deleting platform")
        
        # 4a.3 Obtener todos los menus de la compañía
        menus = await self.menu_list_uc.execute(
            config=config,
            params=Pagination(
                filters=[
                    FilterManager(
                        field="company_id",
                        condition=CONDITION_TYPE.EQUALS,
                        value=str(company_id)
                    )
                ],
                all_data=True
            )
        )
        
        if menus and not isinstance(menus, str):
            # 4a.4 Para cada menu, eliminar permisos y luego el menu
            for menu in menus:
                # Obtener permisos del menu
                menu_permissions = await self.menu_permission_list_uc.execute(
                    config=config,
                    params=Pagination(
                        filters=[
                            FilterManager(
                                field="menu_id",
                                condition=CONDITION_TYPE.EQUALS,
                                value=str(menu.id)
                            )
                        ],
                        all_data=True
                    )
                )
                
                if menu_permissions and not isinstance(menu_permissions, str):
                    for mp in menu_permissions:
                        mp_deleted = await self.menu_permission_delete_uc.execute(
                            config=config,
                            params=MenuPermissionDelete(id=mp.id)
                        )
                        if isinstance(mp_deleted, str):
                            raise Exception("Error deleting menu_permission")
                
                # Eliminar menu
                menu_deleted = await self.menu_delete_uc.execute(
                    config=config,
                    params=MenuDelete(id=menu.id)
                )
                if isinstance(menu_deleted, str):
                    raise Exception("Error deleting menu")
        
        # 4a.5 Eliminar todas las locations
        if locations and not isinstance(locations, str):
            for location in locations:
                location_deleted = await self.location_delete_uc.execute(
                    config=config,
                    params=LocationDelete(id=location.id)
                )
                if isinstance(location_deleted, str):
                    raise Exception("Error deleting location")
        
        # 4a.6 Eliminar company
        company_deleted = await self.company_delete_uc.execute(
            config=config,
            params=CompanyDelete(id=company_id)
        )
        if isinstance(company_deleted, str):
            raise Exception("Error deleting company")

    async def _handle_soft_delete(self, config: Config, company) -> str:
        """Maneja el soft delete y retorna el mensaje correspondiente."""
        soft_delete_result = await self.soft_delete_company_uc.execute(
            config=config,
            company=company
        )
        if isinstance(soft_delete_result, str):
            return soft_delete_result
        
        return await self.message.get_message(
            config=config,
            message=MessageCoreEntity(
                key=KEYS_MESSAGES.DELETE_COMPANY_SOFT_DELETED.value
            ),
        )


from typing import Union
from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.enums.rol_type import ROL_TYPE
from src.core.models.config import Config
from src.core.models.filter import Pagination, FilterManager
from src.core.enums.condition_type import CONDITION_TYPE
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.wrappers.execute_transaction import execute_transaction
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity

from src.domain.models.business.auth.update_user_internal import (
    UpdateUserInternalRequest
)
from src.domain.models.entities.user.index import UserRead, UserUpdate
from src.domain.models.entities.user_location_rol.index import UserLocationRolUpdate
from src.domain.models.entities.rol.index import RolRead

from src.domain.services.use_cases.entities.user.user_read_use_case import (
    UserReadUseCase
)
from src.domain.services.use_cases.entities.user.user_update_use_case import (
    UserUpdateUseCase
)
from src.domain.services.use_cases.entities.user.user_list_use_case import (
    UserListUseCase
)
from src.domain.services.use_cases.entities.user_location_rol.user_location_rol_list_use_case import (
    UserLocationRolListUseCase
)
from src.domain.services.use_cases.entities.user_location_rol.user_location_rol_update_use_case import (
    UserLocationRolUpdateUseCase
)
from src.domain.services.use_cases.entities.rol.rol_read_use_case import (
    RolReadUseCase
)
from src.domain.services.use_cases.entities.rol.rol_list_use_case import (
    RolListUseCase
)

from src.infrastructure.database.repositories.entities.user_repository import (
    UserRepository
)
from src.infrastructure.database.repositories.entities.user_location_rol_repository import (
    UserLocationRolRepository
)
from src.infrastructure.database.repositories.entities.rol_repository import (
    RolRepository
)


user_repository = UserRepository()
user_location_rol_repository = UserLocationRolRepository()
rol_repository = RolRepository()


class UpdateUserInternalUseCase:
    """
    Actualiza un usuario interno existente.
    
    Validaciones:
    1. Usuario existe
    2. No auto-degradación de rol ADMIN
    3. Usuario pertenece a la misma ubicación del admin
    4. Si cambia rol ADMIN, verificar que no sea el último
    5. Rol destino existe (si se envía)
    
    Acciones:
    1. Actualizar datos del usuario (nombre, apellido, teléfono)
    2. Actualizar rol si se envía
    """
    
    def __init__(self):
        self.user_read_uc = UserReadUseCase(user_repository)
        self.user_update_uc = UserUpdateUseCase(user_repository)
        self.user_list_uc = UserListUseCase(user_repository)
        self.user_location_rol_list_uc = UserLocationRolListUseCase(user_location_rol_repository)
        self.user_location_rol_update_uc = UserLocationRolUpdateUseCase(user_location_rol_repository)
        self.rol_read_uc = RolReadUseCase(rol_repository)
        self.rol_list_uc = RolListUseCase(rol_repository)
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        user_id: UUID4,
        params: UpdateUserInternalRequest,
    ) -> Union[str, None]:
        config.response_type = RESPONSE_TYPE.OBJECT

        # 1. Validar que el usuario existe
        user = await self.user_read_uc.execute(
            config=config,
            params=UserRead(id=user_id)
        )
        if isinstance(user, str) or not user:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_UPDATE_USER_NOT_FOUND.value,
                    params={"user_id": str(user_id)}
                ),
            )

        # 2. Obtener user_location_rols del usuario
        user_location_rols = await self.user_location_rol_list_uc.execute(
            config=config,
            params=Pagination(
                filters=[
                    FilterManager(
                        field="user_id",
                        condition=CONDITION_TYPE.EQUALS,
                        value=str(user_id)
                    )
                ]
            )
        )

        if isinstance(user_location_rols, str):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_UPDATE_USER_ERROR_FETCHING_ROLES.value
                ),
            )

        # 3. Validar que el usuario pertenece a la misma ubicación del admin
        admin_location_id = str(config.token.location_id)
        user_ulr_in_location = None
        
        if user_location_rols:
            for ulr in user_location_rols:
                if str(ulr.location_id) == admin_location_id:
                    user_ulr_in_location = ulr
                    break
        
        if not user_ulr_in_location:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_UPDATE_USER_NOT_IN_LOCATION.value
                ),
            )

        # 3.5. Validar email único si se está cambiando
        if params.email is not None and params.email != user.email:
            existing_users = await self.user_list_uc.execute(
                config=config,
                params=Pagination(
                    filters=[
                        FilterManager(
                            field="email",
                            condition=CONDITION_TYPE.EQUALS,
                            value=params.email
                        ),
                        FilterManager(
                            field="id",
                            condition=CONDITION_TYPE.DIFFERENT_THAN,
                            value=str(user_id)
                        )
                    ]
                )
            )
            if existing_users and not isinstance(existing_users, str) and len(existing_users) > 0:
                return await self.message.get_message(
                    config=config,
                    message=MessageCoreEntity(
                        key=KEYS_MESSAGES.AUTH_CREATE_USER_EMAIL_ALREADY_EXISTS.value
                    ),
                )

        # 4. Si se envía rol_id, validar cambio de rol
        if params.rol_id:
            # Validar que el rol destino existe
            new_rol = await self.rol_read_uc.execute(
                config=config,
                params=RolRead(id=params.rol_id)
            )
            if isinstance(new_rol, str) or not new_rol:
                return await self.message.get_message(
                    config=config,
                    message=MessageCoreEntity(
                        key=KEYS_MESSAGES.AUTH_UPDATE_USER_ROL_NOT_FOUND.value
                    ),
                )

            # Obtener el rol ADMIN para comparaciones
            admin_roles = await self.rol_list_uc.execute(
                config=config,
                params=Pagination(
                    filters=[
                        FilterManager(
                            field="code",
                            condition=CONDITION_TYPE.EQUALS,
                            value=ROL_TYPE.ADMIN.value
                        )
                    ]
                )
            )
            
            admin_rol_id = None
            if admin_roles and not isinstance(admin_roles, str) and len(admin_roles) > 0:
                admin_rol_id = str(admin_roles[0].id)

            # Verificar si el usuario actual tiene rol ADMIN
            current_rol_is_admin = admin_rol_id and str(user_ulr_in_location.rol_id) == admin_rol_id
            new_rol_is_admin = admin_rol_id and str(params.rol_id) == admin_rol_id

            # 4a. Si es auto-edición y se intenta quitar rol ADMIN
            if str(user_id) == str(config.token.user_id) and current_rol_is_admin and not new_rol_is_admin:
                return await self.message.get_message(
                    config=config,
                    message=MessageCoreEntity(
                        key=KEYS_MESSAGES.AUTH_UPDATE_USER_CANNOT_DEMOTE_SELF.value
                    ),
                )

            # 4b. Si se cambia de ADMIN a otro rol, verificar que no sea el último
            if current_rol_is_admin and not new_rol_is_admin and admin_rol_id:
                admins_in_location = await self.user_location_rol_list_uc.execute(
                    config=config,
                    params=Pagination(
                        filters=[
                            FilterManager(
                                field="location_id",
                                condition=CONDITION_TYPE.EQUALS,
                                value=admin_location_id
                            ),
                            FilterManager(
                                field="rol_id",
                                condition=CONDITION_TYPE.EQUALS,
                                value=admin_rol_id
                            )
                        ],
                        all_data=True
                    )
                )
                
                if admins_in_location and not isinstance(admins_in_location, str):
                    if len(admins_in_location) <= 1:
                        return await self.message.get_message(
                            config=config,
                            message=MessageCoreEntity(
                                key=KEYS_MESSAGES.AUTH_UPDATE_USER_LAST_ADMIN.value
                            ),
                        )

        # 5. Actualizar datos del usuario
        has_user_changes = (
            params.password is not None or
            params.email is not None or
            params.identification is not None or
            params.first_name is not None or
            params.last_name is not None or
            params.phone is not None or
            params.state is not None
        )
        
        if has_user_changes:
            update_params = UserUpdate(
                id=user.id,
                platform_id=user.platform_id,
                password=params.password if params.password is not None else user.password,
                email=params.email if params.email is not None else user.email,
                identification=params.identification if params.identification is not None else user.identification,
                first_name=params.first_name if params.first_name is not None else user.first_name,
                last_name=params.last_name if params.last_name is not None else user.last_name,
                phone=params.phone if params.phone is not None else user.phone,
                refresh_token=user.refresh_token,
                state=params.state if params.state is not None else user.state
            )
            
            result = await self.user_update_uc.execute(
                config=config,
                params=update_params
            )
            
            if isinstance(result, str):
                return await self.message.get_message(
                    config=config,
                    message=MessageCoreEntity(
                        key=KEYS_MESSAGES.AUTH_UPDATE_USER_ERROR.value
                    ),
                )

        # 6. Actualizar rol si se envió
        if params.rol_id and str(params.rol_id) != str(user_ulr_in_location.rol_id):
            ulr_update_params = UserLocationRolUpdate(
                id=user_ulr_in_location.id,
                user_id=user_ulr_in_location.user_id,
                location_id=user_ulr_in_location.location_id,
                rol_id=params.rol_id,
                state=user_ulr_in_location.state
            )
            
            ulr_result = await self.user_location_rol_update_uc.execute(
                config=config,
                params=ulr_update_params
            )
            
            if isinstance(ulr_result, str):
                return await self.message.get_message(
                    config=config,
                    message=MessageCoreEntity(
                        key=KEYS_MESSAGES.AUTH_UPDATE_USER_ERROR_UPDATING_ROL.value
                    ),
                )

        return None  # Éxito


from typing import Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.login.index import (
    AuthLoginRequest,
    AuthLoginResponse,
)
from src.domain.services.use_cases.business.auth.login.auth_validate_user_use_case import (
    AuthValidateUserUseCase,
)
from src.domain.services.use_cases.business.auth.login.check_user_type_by_rol_use_case import (
    CheckUserTypeByRolUseCase,
)
from src.domain.services.use_cases.business.auth.login.auth_login_use_case import (
    AuthLoginUseCase,
)
from src.domain.services.use_cases.business.auth.login.auth_login_external_use_case import (
    AuthLoginExternalUseCase,
)
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.condition_type import CONDITION_TYPE
from src.core.models.filter import FilterManager, Pagination
from src.domain.services.use_cases.entities.user.user_list_use_case import (
    UserListUseCase,
)
from src.infrastructure.database.repositories.entities.user_repository import (
    UserRepository,
)


user_repository = UserRepository()


class AuthLoginOrchestratorUseCase:
    """
    Orquestador principal de login que detecta el tipo de usuario
    y redirige al flujo correspondiente.
    
    Flujo:
    1. Validar credenciales (email/password)
    2. Obtener el usuario validado
    3. Detectar tipo de usuario por ROL (marca irrefutable)
    4. Redirigir al flujo interno o externo
    """
    
    def __init__(self):
        self.auth_validate_user_use_case = AuthValidateUserUseCase()
        self.check_user_type_by_rol_use_case = CheckUserTypeByRolUseCase()
        self.auth_login_use_case = AuthLoginUseCase()
        self.auth_login_external_use_case = AuthLoginExternalUseCase()
        self.user_list_use_case = UserListUseCase(user_repository)
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: AuthLoginRequest,
    ) -> Union[AuthLoginResponse, str, None]:
        config.response_type = RESPONSE_TYPE.OBJECT

        # 1. Validar credenciales
        user_validation = await self.auth_validate_user_use_case.execute(
            config=config, params=params
        )
        if isinstance(user_validation, str):
            return user_validation

        # 2. Obtener el usuario para tener su ID
        # AuthValidateUserUseCase retorna True si es válido, necesitamos el usuario
        result_users_list = await self.user_list_use_case.execute(
            config=config,
            params=Pagination(
                all_data=True,
                filters=[
                    FilterManager(
                        field="email",
                        condition=CONDITION_TYPE.EQUALS.value,
                        value=params.email,
                    )
                ],
            ),
        )

        if isinstance(result_users_list, str) or not result_users_list:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_RECORD_NOT_FOUND.value
                ),
            )

        [user] = result_users_list

        # 3. Detectar tipo de usuario por ROL (marca irrefutable)
        user_type_info = await self.check_user_type_by_rol_use_case.execute(
            config=config, user_id=user.id
        )

        # 4. Si no tiene rol asignado, retornar error
        # Todos los usuarios deben tener un rol asignado en user_location_rol
        if user_type_info is None:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_RECORD_NOT_FOUND.value
                ),
            )

        # 5. Redirigir al flujo correspondiente basado en el rol
        if user_type_info.is_internal:
            return await self.auth_login_use_case.execute(
                config=config, params=params
            )
        else:
            return await self.auth_login_external_use_case.execute(
                config=config,
                params=params,
                validated_user=user,
            )

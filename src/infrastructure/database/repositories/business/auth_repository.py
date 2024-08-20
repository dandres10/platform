from typing import Any, List, Tuple, Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.auth_login_request import AuthLoginRequest
from src.domain.models.entities.user_location_rol.user_location_rol import UserLocationRol
from src.domain.services.repositories.business.i_auth_repository import IAuthRepository
from src.infrastructure.database.entities.company_entity import CompanyEntity
from src.infrastructure.database.entities.currency_entity import CurrencyEntity
from src.infrastructure.database.entities.currency_location_entity import (
    CurrencyLocationEntity,
)
from src.infrastructure.database.entities.language_entity import LanguageEntity
from src.infrastructure.database.entities.location_entity import LocationEntity
from src.infrastructure.database.entities.platform_entity import PlatformEntity
from src.infrastructure.database.entities.rol_entity import RolEntity
from src.infrastructure.database.entities.user_entity import UserEntity
from src.infrastructure.database.entities.user_location_rol_entity import UserLocationRolEntity


class AuthRepository(IAuthRepository):
    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def login(self, config: Config, params: AuthLoginRequest) -> Union[
        Tuple[
            UserEntity,
            RolEntity,
            PlatformEntity,
            LanguageEntity,
            CurrencyLocationEntity,
            CurrencyEntity,
        ],
        None,
    ]:
        db = config.db

        """ results = (
            db.query(
                PlatformEntity,
                UserEntity,
                LanguageEntity,
                LocationEntity,
                CurrencyLocationEntity,
                CurrencyEntity,
                UserLocationRolEntity,
                RolEntity
            )
            .join(PlatformEntity, PlatformEntity.id == UserEntity.platform_id)
            .join(LanguageEntity, LanguageEntity.id == PlatformEntity.language_id)
            .join(LocationEntity, LocationEntity.id == PlatformEntity.location_id)
            .join(CurrencyLocationEntity, CurrencyLocationEntity.id == PlatformEntity.currency_location_id)
            .join(CurrencyEntity, CurrencyEntity.id == CurrencyLocationEntity.currency_id)
            .join(UserLocationRolEntity, UserLocationRolEntity.user_id == UserEntity.id)
            .join(UserLocationRolEntity, UserLocationRolEntity.rol_id == RolEntity.id)
            .join(UserLocationRolEntity, UserLocationRolEntity.location_id == LocationEntity.id)
            .filter(UserEntity, UserEntity.email == params.email)
            .first()
        ) """

        pass


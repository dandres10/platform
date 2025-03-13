from typing import Any, List, Tuple, Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from sqlalchemy.future import select
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.create_api_token.create_api_token_request import (
    CreateApiTokenRequest,
)
from src.domain.models.business.auth.create_api_token.create_api_token_response import (
    CreateApiTokenResponse,
)
from src.domain.models.business.auth.login.auth_currencies_by_location import (
    AuthCurremciesByLocation,
)
from src.domain.models.business.auth.login.auth_initial_user_data import (
    AuthInitialUserData,
)
from src.domain.models.business.auth.login.auth_locations import AuthLocations
from src.domain.models.business.auth.login.auth_login_request import AuthLoginRequest
from src.domain.models.business.auth.login.auth_user_role_and_permissions import (
    AuthUserRoleAndPermissions,
)
from src.domain.models.business.auth.login.companies_by_user import CompaniesByUser
from src.domain.models.business.auth.login.menu import Menu
from src.domain.models.entities.company.company import Company
from src.domain.services.repositories.business.i_auth_repository import IAuthRepository
from src.infrastructure.database.entities.company_entity import CompanyEntity
from src.infrastructure.database.entities.country_entity import CountryEntity
from src.infrastructure.database.entities.currency_entity import CurrencyEntity
from src.infrastructure.database.entities.currency_location_entity import (
    CurrencyLocationEntity,
)
from src.infrastructure.database.entities.language_entity import LanguageEntity
from src.infrastructure.database.entities.location_entity import LocationEntity
from src.infrastructure.database.entities.menu_entity import MenuEntity
from src.infrastructure.database.entities.menu_permission_entity import (
    MenuPermissionEntity,
)
from src.infrastructure.database.entities.permission_entity import PermissionEntity
from src.infrastructure.database.entities.platform_entity import PlatformEntity
from src.infrastructure.database.entities.rol_entity import RolEntity
from src.infrastructure.database.entities.rol_permission_entity import (
    RolPermissionEntity,
)
from src.infrastructure.database.entities.user_entity import UserEntity
from src.infrastructure.database.entities.user_location_rol_entity import (
    UserLocationRolEntity,
)
from src.infrastructure.database.mappers.company_mapper import map_to_list_company
from src.infrastructure.database.repositories.business.mappers.auth.login.login_mapper import (
    map_to_company_login_response,
)


class AuthRepository(IAuthRepository):
    async def initial_user_data(
        self, config: Config, params: AuthInitialUserData
    ) -> Union[
        Tuple[
            PlatformEntity,
            UserEntity,
            LanguageEntity,
            LocationEntity,
            CurrencyEntity,
            CountryEntity,
            CompanyEntity,
        ],
        None,
    ]:
        async with config.async_db as db:  # Usar AsyncSession de config
            stmt = (
                select(
                    PlatformEntity,
                    UserEntity,
                    LanguageEntity,
                    LocationEntity,
                    CurrencyEntity,
                    CountryEntity,
                    CompanyEntity,
                )
                .join(PlatformEntity, PlatformEntity.id == UserEntity.platform_id)
                .join(LanguageEntity, LanguageEntity.id == PlatformEntity.language_id)
                .join(LocationEntity, LocationEntity.id == PlatformEntity.location_id)
                .join(CurrencyEntity, CurrencyEntity.id == PlatformEntity.currency_id)
                .join(CountryEntity, CountryEntity.id == LocationEntity.country_id)
                .join(CompanyEntity, CompanyEntity.id == LocationEntity.company_id)
                .filter(UserEntity.email == params.email)
                .filter(UserEntity.state == True)
            )

            result = await db.execute(stmt)
            results = result.first()

            return results

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def user_role_and_permissions(
        self, config: Config, params: AuthUserRoleAndPermissions
    ) -> Union[
        List[
            Tuple[
                UserLocationRolEntity,
                UserEntity,
                RolEntity,
                RolPermissionEntity,
                PermissionEntity,
            ]
        ],
        None,
    ]:
        async with config.async_db as db:
            stmt = (
                select(
                    UserLocationRolEntity,
                    UserEntity,
                    RolEntity,
                    RolPermissionEntity,
                    PermissionEntity,
                )
                .join(
                    UserLocationRolEntity,
                    UserLocationRolEntity.user_id == UserEntity.id,
                )
                .join(
                    LocationEntity,
                    LocationEntity.id == UserLocationRolEntity.location_id,
                )
                .join(RolEntity, RolEntity.id == UserLocationRolEntity.rol_id)
                .join(
                    RolPermissionEntity,
                    RolPermissionEntity.rol_id == UserLocationRolEntity.rol_id,
                )
                .join(
                    PermissionEntity,
                    PermissionEntity.id == RolPermissionEntity.permission_id,
                )
                .filter(UserEntity.email == params.email)
                .filter(UserEntity.state == True)
                .filter(LocationEntity.id == params.location)
            )

            result = await db.execute(stmt)
            results = result.all()

            return results

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def menu(self, config: Config, params: Menu) -> Union[
        List[Tuple[MenuPermissionEntity, MenuEntity]],
        None,
    ]:
        async with config.async_db as db:
            stmt = (
                select(MenuPermissionEntity, MenuEntity)
                .join(
                    MenuPermissionEntity, MenuPermissionEntity.menu_id == MenuEntity.id
                )
                .filter(MenuEntity.company_id == params.company)
            )

            result = await db.execute(stmt)
            results = result.all()

            return results

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def currencies_by_location(
        self, config: Config, params: AuthCurremciesByLocation
    ) -> Union[
        List[Tuple[CurrencyLocationEntity, CurrencyEntity, LocationEntity]],
        None,
    ]:
        async with config.async_db as db:
            stmt = (
                select(CurrencyLocationEntity, CurrencyEntity, LocationEntity)
                .join(
                    CurrencyLocationEntity,
                    CurrencyLocationEntity.currency_id == CurrencyEntity.id,
                )
                .join(
                    LocationEntity,
                    LocationEntity.id == CurrencyLocationEntity.location_id,
                )
                .filter(LocationEntity.id == params.location)
            )

            result = await db.execute(stmt)
            results = result.all()

            return results

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def locations_by_user(self, config: Config, params: AuthLocations) -> Union[
        List[Tuple[UserLocationRolEntity, LocationEntity, CompanyEntity, UserEntity]],
        None,
    ]:
        async with config.async_db as db:
            stmt = (
                select(UserLocationRolEntity, LocationEntity, CompanyEntity, UserEntity)
                .join(
                    UserLocationRolEntity,
                    UserLocationRolEntity.location_id == LocationEntity.id,
                )
                .join(CompanyEntity, CompanyEntity.id == LocationEntity.company_id)
                .join(UserEntity, UserEntity.id == UserLocationRolEntity.user_id)
                .filter(UserEntity.id == params.user_id)
                .filter(CompanyEntity.id == params.company_id)
            )

            result = await db.execute(stmt)
            results = result.all()

            return results

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def create_api_token(
        self, config: Config, params: CreateApiTokenRequest
    ) -> Union[
        CreateApiTokenResponse,
        None,
    ]:
        async with config.async_db as db:
            permissions: List[str] = []
            stmt = (
                select(RolPermissionEntity, PermissionEntity)
                .join(
                    RolPermissionEntity,
                    RolPermissionEntity.permission_id == PermissionEntity.id,
                )
                .where(RolPermissionEntity.rol_id == params.rol_id)
            )

            result = await db.execute(stmt)
            results = result.all()

            if not results:
                return None

            for rol_permission, permission in results:
                permissions.append(permission.name)

            stmt = select(RolEntity).where(RolEntity.id == params.rol_id).limit(1)

            result = await db.execute(stmt)
            rol_tuple = result.first()
            rol, *list = rol_tuple

            return CreateApiTokenResponse(
                rol_id=params.rol_id, permissions=permissions, rol_code=rol.code
            )

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def companies_by_user(self, config: Config, params: CompaniesByUser) -> Union[
        List[Company],
        None,
    ]:
        async with config.async_db as db:

            stmt = (
                select(CompanyEntity)
                .join(
                    LocationEntity,  # Agregar LocationEntity a los JOIN
                    CompanyEntity.id == LocationEntity.company_id,
                )
                .join(
                    UserLocationRolEntity,
                    UserLocationRolEntity.location_id == LocationEntity.id,
                )
                .join(
                    UserEntity,
                    UserEntity.id == UserLocationRolEntity.user_id,
                )
                .filter(UserEntity.email == params.email)
                .filter(UserEntity.state == True)
                .distinct(CompanyEntity.id)
            )

            result = await db.execute(stmt)
            company_entities = result.scalars().all()

            if not company_entities:
                return None

            companies = [
                map_to_company_login_response(company) for company in company_entities
            ]

            return companies

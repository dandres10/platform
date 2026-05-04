from typing import Any, List, Optional, Tuple, Union
from uuid import UUID
import hashlib
from src.core.config import settings
from src.core.enums.layer import LAYER
from sqlalchemy.future import select
from sqlalchemy import text
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.wrappers.execute_transaction import execute_transaction
from src.core.methods.apply_memory_filters import apply_memory_filters
from src.core.methods.build_alias_map import build_alias_map

from src.domain.models.business.auth.create_api_token.create_api_token_request import (
    CreateApiTokenRequest,
)
from src.domain.models.business.auth.create_api_token.create_api_token_response import (
    CreateApiTokenResponse,
)
from src.domain.models.business.auth.list_users_by_location import UserByLocationItem
from src.domain.models.business.auth.list_users_external import UserExternalItem
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
from src.domain.models.business.auth.login.user_rol_info import UserRolInfo
from src.domain.models.entities.company.company import Company
from src.domain.models.entities.currency.currency import Currency
from src.domain.models.entities.geo_division.geo_division import GeoDivision
from src.domain.models.entities.language.language import Language
from src.domain.models.entities.location.location import Location
from src.domain.models.entities.platform.platform import Platform
from src.domain.models.entities.user.user import User
from src.domain.services.repositories.business.i_auth_repository import IAuthRepository
from src.infrastructure.database.entities.company_entity import CompanyEntity
from src.infrastructure.database.entities.geo_division_entity import GeoDivisionEntity
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
from src.infrastructure.database.mappers.company_mapper import map_to_company, map_to_list_company
from src.infrastructure.database.mappers.currency_mapper import map_to_currency
from src.infrastructure.database.mappers.geo_division_mapper import map_to_geo_division
from src.infrastructure.database.mappers.language_mapper import map_to_language
from src.infrastructure.database.mappers.location_mapper import map_to_location
from src.infrastructure.database.mappers.platform_mapper import map_to_platform
from src.infrastructure.database.mappers.user_mapper import map_to_user
from src.domain.models.business.auth.login.auth_login_response import (
    CurrencyLoginResponse,
    LocationLoginResponse,
    MenuLoginResponse,
    PermissionLoginResponse,
    RolLoginResponse,
)
from src.domain.models.entities.menu_permission.menu_permission import MenuPermission
from src.infrastructure.database.repositories.business.mappers.auth.login.login_mapper import (
    map_to_company_login_response,
    map_to_currecy_login_response,
    map_to_location_login_response,
    map_to_menu_response,
    map_to_permission_response,
    map_to_rol_login_response,
)
from src.infrastructure.database.repositories.business.mappers.auth.users_internal import (
    map_to_user_by_location_item,
)
from src.infrastructure.database.repositories.business.mappers.auth.users_external import (
    map_to_user_external_item,
)


class AuthRepository(IAuthRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def acquire_company_nit_lock(self, config: Config, nit: str) -> None:
        """SPEC-007: lock por NIT para serializar create_company concurrente."""
        db = config.async_db
        lock_key = int(hashlib.md5(f"company:nit:{nit}".encode()).hexdigest(), 16) % (2**31 - 1)
        await db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": lock_key})

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def acquire_user_email_lock(self, config: Config, email: str) -> None:
        """SPEC-007: lock por email para serializar creación de usuarios concurrente."""
        db = config.async_db
        lock_key = int(hashlib.md5(f"user:email:{email}".encode()).hexdigest(), 16) % (2**31 - 1)
        await db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": lock_key})

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def acquire_api_token_rol_lock(self, config: Config, rol_id) -> None:
        """SPEC-007: lock por rol_id para serializar create_api_token concurrente."""
        db = config.async_db
        lock_key = int(hashlib.md5(f"api_token:rol:{rol_id}".encode()).hexdigest(), 16) % (2**31 - 1)
        await db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": lock_key})

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def acquire_location_admin_lock(self, config: Config, location_id) -> None:
        """SPEC-007: lock por location_id para serializar update/delete del último admin."""
        db = config.async_db
        lock_key = int(hashlib.md5(f"location:admin:{location_id}".encode()).hexdigest(), 16) % (2**31 - 1)
        await db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": lock_key})

    async def initial_user_data(
        self, config: Config, params: AuthInitialUserData
    ) -> Optional[Tuple[Platform, User, Language, Location, Currency, GeoDivision, Company]]:
        db = config.async_db
        stmt = (
            select(
                PlatformEntity,
                UserEntity,
                LanguageEntity,
                LocationEntity,
                CurrencyEntity,
                GeoDivisionEntity,
                CompanyEntity,
            )
            .join(PlatformEntity, PlatformEntity.id == UserEntity.platform_id)
            .join(LanguageEntity, LanguageEntity.id == PlatformEntity.language_id)
            .join(LocationEntity, LocationEntity.id == PlatformEntity.location_id)
            .join(CurrencyEntity, CurrencyEntity.id == PlatformEntity.currency_id)
            .join(GeoDivisionEntity, GeoDivisionEntity.id == LocationEntity.country_id)
            .join(CompanyEntity, CompanyEntity.id == LocationEntity.company_id)
            .filter(UserEntity.email == params.email)
            .filter(UserEntity.state == True)
        )

        result = await db.execute(stmt)
        row = result.first()
        if not row:
            return None

        # SPEC-015 T7
        platform_e, user_e, language_e, location_e, currency_e, geo_e, company_e = row
        return (
            map_to_platform(platform_entity=platform_e),
            map_to_user(user_entity=user_e),
            map_to_language(language_entity=language_e),
            map_to_location(location_entity=location_e),
            map_to_currency(currency_entity=currency_e),
            map_to_geo_division(entity=geo_e),
            map_to_company(company_entity=company_e),
        )

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def user_role_and_permissions(
        self, config: Config, params: AuthUserRoleAndPermissions
    ) -> Optional[Tuple[List[PermissionLoginResponse], RolLoginResponse]]:
        db = config.async_db
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

        if not results:
            return None

        # SPEC-015 T3
        permissions = [
            map_to_permission_response(permission_entity=row[4]) for row in results
        ]
        rol = map_to_rol_login_response(rol_entity=results[0][2])
        return (permissions, rol)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def menu(
        self, config: Config, params: Menu
    ) -> Optional[Tuple[List[MenuPermission], List[MenuLoginResponse]]]:
        """
        Obtiene menús para usuarios internos. Solo type='INTERNAL'.
        """
        db = config.async_db
        stmt = (
            select(MenuPermissionEntity, MenuEntity)
            .join(
                MenuPermissionEntity, MenuPermissionEntity.menu_id == MenuEntity.id
            )
            .filter(MenuEntity.company_id == params.company)
            .filter(MenuEntity.type == "INTERNAL")
            .filter(MenuEntity.state == True)
        )

        result = await db.execute(stmt)
        rows = result.all()

        if not rows:
            return None

        # SPEC-015 T5
        menu_permissions: List[MenuPermission] = []
        menus_by_id: dict = {}
        for menu_permission_entity, menu_entity in rows:
            menu_permissions.append(
                MenuPermission(
                    id=menu_permission_entity.id,
                    menu_id=menu_permission_entity.menu_id,
                    permission_id=menu_permission_entity.permission_id,
                    state=menu_permission_entity.state,
                )
            )
            if menu_entity.id not in menus_by_id:
                menus_by_id[menu_entity.id] = map_to_menu_response(menu_entity=menu_entity)

        return (menu_permissions, list(menus_by_id.values()))

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def currencies_by_location(
        self, config: Config, params: AuthCurremciesByLocation
    ) -> Optional[List[CurrencyLoginResponse]]:
        db = config.async_db
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

        if not results:
            return None

        # SPEC-019
        return [
            map_to_currecy_login_response(currency_entity=row[1]) for row in results
        ]

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def locations_by_user(
        self, config: Config, params: AuthLocations
    ) -> Optional[List[LocationLoginResponse]]:
        db = config.async_db
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

        if not results:
            return None

        # SPEC-019
        return [
            map_to_location_login_response(location_entity=row[1]) for row in results
        ]

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def create_api_token(
        self, config: Config, params: CreateApiTokenRequest
    ) -> Union[
        CreateApiTokenResponse,
        None,
    ]:
        db = config.async_db
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
        # SPEC-030 T7
        rol, *_ = rol_tuple

        return CreateApiTokenResponse(
            rol_id=params.rol_id, permissions=permissions, rol_code=rol.code
        )

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def companies_by_user(self, config: Config, params: CompaniesByUser) -> Union[
        List[Company],
        None,
    ]:
        db = config.async_db

        stmt = (
            select(CompanyEntity)
            .join(
                LocationEntity,
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

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def users_internal(
        self, config: Config, params: Pagination
    ) -> Union[List[UserByLocationItem], None]:
        db = config.async_db
        stmt = (
            select(
                UserLocationRolEntity.id.label("user_location_rol_id"),
                UserLocationRolEntity.location_id.label("location_id"),
                UserEntity.id.label("user_id"),
                UserEntity.email,
                UserEntity.identification,
                UserEntity.first_name,
                UserEntity.last_name,
                UserEntity.phone,
                UserEntity.state.label("user_state"),
                UserEntity.created_date.label("user_created_date"),
                UserEntity.updated_date.label("user_updated_date"),
                RolEntity.id.label("rol_id"),
                RolEntity.name.label("rol_name"),
                RolEntity.code.label("rol_code"),
                RolEntity.description.label("rol_description"),
            )
            .join(UserEntity, UserLocationRolEntity.user_id == UserEntity.id)
            .join(RolEntity, UserLocationRolEntity.rol_id == RolEntity.id)
            .filter(UserLocationRolEntity.state == True)
            .order_by(UserEntity.first_name, UserEntity.last_name)
        )

        if not params.filters and not params.all_data:
            stmt = stmt.offset(params.skip).limit(params.limit)

        result = await db.execute(stmt)
        results = result.all()

        if not results:
            return None

        users_internal: List[UserByLocationItem] = [
            map_to_user_by_location_item(row) for row in results
        ]

        if params.filters:
            alias_map = build_alias_map(response_class=UserByLocationItem)

            users_internal = [
                user
                for user in users_internal
                if apply_memory_filters(user, params.filters, alias_map)
            ]

            if not params.all_data:
                skip = params.skip if params.skip is not None else 0
                limit = params.limit if params.limit is not None else 10
                users_internal = users_internal[skip : skip + limit]

        return users_internal

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def users_external(
        self, config: Config, params: Pagination
    ) -> Union[List[UserExternalItem], None]:
        db = config.async_db
        stmt = (
            select(
                PlatformEntity.id.label("platform_id"),
                UserEntity.id.label("user_id"),
                UserEntity.email,
                UserEntity.identification,
                UserEntity.first_name,
                UserEntity.last_name,
                UserEntity.phone,
                UserEntity.state.label("user_state"),
                UserEntity.created_date.label("user_created_date"),
                UserEntity.updated_date.label("user_updated_date"),
                PlatformEntity.language_id,
                PlatformEntity.currency_id,
                PlatformEntity.token_expiration_minutes,
                PlatformEntity.refresh_token_expiration_minutes,
                PlatformEntity.created_date.label("platform_created_date"),
                PlatformEntity.updated_date.label("platform_updated_date"),
            )
            .join(PlatformEntity, UserEntity.platform_id == PlatformEntity.id)
            .outerjoin(UserLocationRolEntity, UserEntity.id == UserLocationRolEntity.user_id)
            .filter(UserEntity.state == True)
            .filter(PlatformEntity.location_id.is_(None))
            .filter(UserLocationRolEntity.id.is_(None))
            .order_by(UserEntity.first_name, UserEntity.last_name)
        )

        if not params.filters and not params.all_data:
            stmt = stmt.offset(params.skip).limit(params.limit)

        result = await db.execute(stmt)
        results = result.all()

        if not results:
            return None

        users_external: List[UserExternalItem] = [
            map_to_user_external_item(row) for row in results
        ]

        if params.filters:
            alias_map = build_alias_map(response_class=UserExternalItem)

            users_external = [
                user
                for user in users_external
                if apply_memory_filters(user, params.filters, alias_map)
            ]

            if not params.all_data:
                skip = params.skip if params.skip is not None else 0
                limit = params.limit if params.limit is not None else 10
                users_external = users_external[skip : skip + limit]

        return users_external

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def get_user_rol_info(
        self, config: Config, user_id: UUID
    ) -> Optional[UserRolInfo]:
        """
        Obtiene información del rol del usuario desde user_location_rol.
        
        Todos los usuarios (internos y externos) deben tener un registro aquí.
        Para usuarios externos, location_id será NULL pero el rol estará asignado.
        
        Args:
            config: Configuración de la solicitud
            user_id: ID del usuario
            
        Returns:
            UserRolInfo con rol_id y rol_code si existe
            None si el usuario no tiene rol asignado
        """
        db = config.async_db
        stmt = (
            select(
                UserLocationRolEntity.rol_id,
                RolEntity.code.label('rol_code')
            )
            .join(RolEntity, UserLocationRolEntity.rol_id == RolEntity.id)
            .filter(UserLocationRolEntity.user_id == user_id)
            .filter(UserLocationRolEntity.state == True)
        )

        result = await db.execute(stmt)
        row = result.first()

        if row is None:
            return None

        return UserRolInfo(
            rol_id=row.rol_id,
            rol_code=row.rol_code
        )

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def initial_external_user_data(
        self, config: Config, email: str
    ) -> Optional[Tuple[Platform, User, Language, Currency]]:
        """Datos iniciales de un usuario externo (sin location, country ni company)."""
        db = config.async_db
        stmt = (
            select(PlatformEntity, UserEntity, LanguageEntity, CurrencyEntity)
            .join(PlatformEntity, PlatformEntity.id == UserEntity.platform_id)
            .join(LanguageEntity, LanguageEntity.id == PlatformEntity.language_id)
            .join(CurrencyEntity, CurrencyEntity.id == PlatformEntity.currency_id)
            .filter(UserEntity.email == email)
            .filter(UserEntity.state == True)
            .filter(PlatformEntity.location_id.is_(None))
        )

        result = await db.execute(stmt)
        row = result.first()
        if not row:
            return None

        # SPEC-015 T6
        platform_entity, user_entity, language_entity, currency_entity = row
        return (
            map_to_platform(platform_entity=platform_entity),
            map_to_user(user_entity=user_entity),
            map_to_language(language_entity=language_entity),
            map_to_currency(currency_entity=currency_entity),
        )

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def external_rol_and_permissions_by_code(
        self, config: Config, rol_code: str
    ) -> Optional[Tuple[List[PermissionLoginResponse], RolLoginResponse]]:
        db = config.async_db
        stmt = (
            select(RolEntity, RolPermissionEntity, PermissionEntity)
            .join(RolPermissionEntity, RolPermissionEntity.rol_id == RolEntity.id)
            .join(PermissionEntity, PermissionEntity.id == RolPermissionEntity.permission_id)
            .filter(RolEntity.code == rol_code)
            .filter(RolEntity.state == True)
        )

        result = await db.execute(stmt)
        rows = result.all()

        if not rows:
            return None

        # SPEC-015 T4
        seen_permission_ids = set()
        permissions: List[PermissionLoginResponse] = []
        for _, _, permission_entity in rows:
            if permission_entity.id not in seen_permission_ids:
                seen_permission_ids.add(permission_entity.id)
                permissions.append(map_to_permission_response(permission_entity=permission_entity))

        rol = map_to_rol_login_response(rol_entity=rows[0][0])
        return (permissions, rol)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def menu_external(
        self, config: Config, permission_ids: List[str]
    ) -> Optional[List[MenuLoginResponse]]:
        """
        Obtiene menús para usuarios externos.
        
        Solo retorna menús con type='EXTERNAL' asociados a los permisos dados.
        
        Args:
            config: Configuración de la solicitud
            permission_ids: Lista de IDs de permisos del rol
            
        Returns:
            Lista de MenuLoginResponse (deduplicada por menu_id)
            None si no se encuentra
        """
        db = config.async_db
        stmt = (
            select(MenuPermissionEntity, MenuEntity)
            .join(MenuPermissionEntity, MenuPermissionEntity.menu_id == MenuEntity.id)
            .filter(MenuEntity.type == "EXTERNAL")
            .filter(MenuPermissionEntity.permission_id.in_(permission_ids))
            .filter(MenuEntity.state == True)
        )

        result = await db.execute(stmt)
        rows = result.all()

        if not rows:
            return None

        # SPEC-019
        seen_menu_ids = set()
        menus: List[MenuLoginResponse] = []
        for _, menu_entity in rows:
            if menu_entity.id not in seen_menu_ids:
                seen_menu_ids.add(menu_entity.id)
                menus.append(map_to_menu_response(menu_entity=menu_entity))
        return menus

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def all_currencies(
        self, config: Config
    ) -> Optional[List[CurrencyLoginResponse]]:
        """
        Obtiene todas las currencies activas del sistema.
        
        Se usa para usuarios externos que no tienen currencies por location.
        
        Args:
            config: Configuración de la solicitud
            
        Returns:
            Lista de CurrencyLoginResponse activas
            None si no hay currencies
        """
        db = config.async_db
        stmt = (
            select(CurrencyEntity)
            .filter(CurrencyEntity.state == True)
            .order_by(CurrencyEntity.name)
        )

        result = await db.execute(stmt)
        currencies = result.scalars().all()

        if not currencies:
            return None

        # SPEC-019
        return [
            map_to_currecy_login_response(currency_entity=currency)
            for currency in currencies
        ]

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def user_country(
        self, config: Config, user_id: UUID
    ) -> Union[GeoDivisionEntity, None]:
        """
        Obtiene el país asociado a un usuario externo desde user_country.
        
        user_country.country_id ahora apunta a geo_division(id) con tipo COUNTRY.
        
        Args:
            config: Configuración de la solicitud
            user_id: ID del usuario
            
        Returns:
            GeoDivisionEntity (tipo COUNTRY) si el usuario tiene país asociado
            None si no tiene
        """
        from src.infrastructure.database.entities.user_country_entity import (
            UserCountryEntity,
        )
        
        db = config.async_db
        stmt = (
            select(GeoDivisionEntity)
            .join(UserCountryEntity, UserCountryEntity.country_id == GeoDivisionEntity.id)
            .filter(UserCountryEntity.user_id == user_id)
            .filter(UserCountryEntity.state == True)
            .filter(GeoDivisionEntity.state == True)
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

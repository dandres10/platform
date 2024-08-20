from typing import List
from src.domain.models.business.auth.auth_login_response import (
    CompanyLoginResponse,
    CountryLoginResponse,
    CurrecyLoginResponse,
    LanguageLoginResponse,
    LocationLoginResponse,
    PermissionLoginResponse,
    PlatformLoginResponse,
    RolLoginResponse,
    UserLoginResponse,
)
from src.infrastructure.database.entities.company_entity import CompanyEntity
from src.infrastructure.database.entities.country_entity import CountryEntity
from src.infrastructure.database.entities.currency_entity import CurrencyEntity
from src.infrastructure.database.entities.language_entity import LanguageEntity
from src.infrastructure.database.entities.location_entity import LocationEntity
from src.infrastructure.database.entities.permission_entity import PermissionEntity
from src.infrastructure.database.entities.platform_entity import PlatformEntity
from src.infrastructure.database.entities.rol_entity import RolEntity
from src.infrastructure.database.entities.user_entity import UserEntity


def map_to_user_login_response(user_entity: UserEntity) -> UserLoginResponse:
    return UserLoginResponse(
        id=user_entity.id,
        email=user_entity.email,
        first_name=user_entity.first_name,
        last_name=user_entity.last_name,
        phone=user_entity.phone,
        state=user_entity.state,
    )


""" def map_to_list_user_login_response(
    user_entities: List[UserEntity],
) -> List[UserLoginResponse]:
    return [map_to_user_login_response(user) for user in user_entities] """


def map_to_currecy_login_response(
    currency_entity: CurrencyEntity,
) -> CurrecyLoginResponse:
    return CurrecyLoginResponse(
        id=currency_entity.id,
        name=currency_entity.name,
        code=currency_entity.code,
        symbol=currency_entity.symbol,
        state=currency_entity.state,
    )


def map_to_location_login_response(
    location_entity: LocationEntity,
) -> LocationLoginResponse:
    return LocationLoginResponse(
        id=location_entity.id,
        name=location_entity.name,
        address=location_entity.address,
        city=location_entity.city,
        phone=location_entity.phone,
        email=location_entity.email,
        main_location=location_entity.main_location,
        state=location_entity.state,
    )


def map_to_language_login_response(
    language_entity: LanguageEntity,
) -> LanguageLoginResponse:
    return LanguageLoginResponse(
        id=language_entity.id,
        name=language_entity.name,
        code=language_entity.code,
        native_name=language_entity.native_name,
        state=language_entity.state,
    )


def map_to_platform_login_response(
    platform_entity: PlatformEntity,
) -> PlatformLoginResponse:
    return PlatformLoginResponse(
        id=platform_entity.id,
        language_id=platform_entity.language_id,
        location_id=platform_entity.location_id,
        token_expiration_minutes=platform_entity.token_expiration_minutes,
        currency_id=platform_entity.currency_id,
    )


def map_to_country_login_response(
    country_entity: CountryEntity,
) -> CountryLoginResponse:
    return CountryLoginResponse(
        id=country_entity.id,
        name=country_entity.name,
        code=country_entity.code,
        phone_code=country_entity.phone_code,
        state=country_entity.state,
    )


def map_to_company_login_response(
    company_entity: CompanyEntity,
) -> CompanyLoginResponse:
    return CompanyLoginResponse(
        id=company_entity.id,
        name=company_entity.name,
        inactivity_time=company_entity.inactivity_time,
        nit=company_entity.nit,
        state=company_entity.state,
    )


def map_to_rol_login_response(
    rol_entity: RolEntity,
) -> RolLoginResponse:
    return RolLoginResponse(
        id=rol_entity.id,
        name=rol_entity.name,
        code=rol_entity.code,
        description=rol_entity.description,
        state=rol_entity.state,
    )


def map_to_permission_response(
    permission_entity: PermissionEntity,
) -> PermissionLoginResponse:
    return PermissionLoginResponse(
        id=permission_entity.id,
        name=permission_entity.name,
        description=permission_entity.description,
        state=permission_entity.state,
    )

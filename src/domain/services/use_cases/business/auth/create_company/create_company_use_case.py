from typing import Union
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

from src.domain.models.business.auth.create_company.index import CreateCompanyRequest
from src.domain.models.entities.company.index import CompanySave
from src.domain.models.entities.location.index import LocationSave
from src.domain.models.entities.country.index import CountryRead
from src.domain.models.entities.language.index import LanguageRead
from src.domain.models.entities.currency.index import CurrencyRead
from src.domain.models.entities.currency_location.index import CurrencyLocationSave
from src.domain.models.entities.rol.index import RolRead
from src.domain.models.business.auth.create_user_internal.index import (
    CreateUserInternalRequest,
    LocationRolItem
)

# Importar repositorios
from src.infrastructure.database.repositories.entities.company_repository import CompanyRepository
from src.infrastructure.database.repositories.entities.country_repository import CountryRepository
from src.infrastructure.database.repositories.entities.language_repository import LanguageRepository
from src.infrastructure.database.repositories.entities.currency_repository import CurrencyRepository
from src.infrastructure.database.repositories.entities.rol_repository import RolRepository
from src.infrastructure.database.repositories.entities.user_repository import UserRepository
from src.infrastructure.database.repositories.entities.menu_repository import MenuRepository
from src.infrastructure.database.repositories.entities.location_repository import LocationRepository
from src.infrastructure.database.repositories.entities.currency_location_repository import CurrencyLocationRepository

# Importar use cases de entidades
from src.domain.services.use_cases.entities.company.company_save_use_case import CompanySaveUseCase
from src.domain.services.use_cases.entities.company.company_list_use_case import CompanyListUseCase
from src.domain.services.use_cases.entities.country.country_read_use_case import CountryReadUseCase
from src.domain.services.use_cases.entities.language.language_read_use_case import LanguageReadUseCase
from src.domain.services.use_cases.entities.currency.currency_read_use_case import CurrencyReadUseCase
from src.domain.services.use_cases.entities.rol.rol_read_use_case import RolReadUseCase
from src.domain.services.use_cases.entities.user.user_list_use_case import UserListUseCase
from src.domain.services.use_cases.entities.menu.menu_list_use_case import MenuListUseCase
from src.domain.services.use_cases.entities.location.location_save_use_case import LocationSaveUseCase
from src.domain.services.use_cases.entities.currency_location.currency_location_save_use_case import CurrencyLocationSaveUseCase
from src.domain.services.use_cases.business.auth.create_user_internal.create_user_internal_use_case import CreateUserInternalUseCase

# Importar casos de uso auxiliares (misma carpeta - imports relativos)
from .clone_menus_for_company_use_case import CloneMenusForCompanyUseCase
from .clone_menu_permissions_for_company_use_case import CloneMenuPermissionsForCompanyUseCase

# Instanciar repositorios
company_repository = CompanyRepository()
country_repository = CountryRepository()
language_repository = LanguageRepository()
currency_repository = CurrencyRepository()
rol_repository = RolRepository()
user_repository = UserRepository()
menu_repository = MenuRepository()
location_repository = LocationRepository()
currency_location_repository = CurrencyLocationRepository()


class CreateCompanyUseCase:
    """
    Use Case para crear una compañía completa en el sistema.
    
    Proceso:
    1. Validar todas las referencias (NIT, email, country, language, currency, rol, templates)
    2. Crear Company
    3. Clonar menús template manteniendo jerarquías (usando caso de uso auxiliar)
    4. Clonar permisos de menús (usando caso de uso auxiliar)
    5. Crear Location principal
    6. Crear CurrencyLocation (asociar moneda a la ubicación)
    7. Crear User admin inicial (reutilizando CreateUserInternalUseCase)
    8. Retornar mensaje de éxito traducido
    """
    
    def __init__(self):
        # Use cases de validación
        self.company_list_uc = CompanyListUseCase(company_repository)
        self.country_read_uc = CountryReadUseCase(country_repository)
        self.language_read_uc = LanguageReadUseCase(language_repository)
        self.currency_read_uc = CurrencyReadUseCase(currency_repository)
        self.rol_read_uc = RolReadUseCase(rol_repository)
        self.user_list_uc = UserListUseCase(user_repository)
        self.menu_list_uc = MenuListUseCase(menu_repository)
        
        # Use cases de creación
        self.company_save_uc = CompanySaveUseCase(company_repository)
        self.location_save_uc = LocationSaveUseCase(location_repository)
        self.currency_location_save_uc = CurrencyLocationSaveUseCase(currency_location_repository)
        self.create_user_internal_uc = CreateUserInternalUseCase()
        
        # Use cases auxiliares (misma carpeta)
        self.clone_menus_uc = CloneMenusForCompanyUseCase()
        self.clone_permissions_uc = CloneMenuPermissionsForCompanyUseCase()
        
        self.message = Message()
    
    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: CreateCompanyRequest,
    ) -> Union[str, None]:
        config.response_type = RESPONSE_TYPE.OBJECT
        
        # ============================================
        # 1. VALIDACIONES PREVIAS
        # ============================================
        
        # Validar NIT único
        existing_companies = await self.company_list_uc.execute(
            config=config,
            params=Pagination(filters=[
                FilterManager(
                    field="nit",
                    value=params.company.nit,
                    condition=CONDITION_TYPE.EQUALS
                )
            ])
        )
        if existing_companies and not isinstance(existing_companies, str):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CREATE_COMPANY_NIT_ALREADY_EXISTS.value
                ),
            )
        
        # Validar email único
        existing_users = await self.user_list_uc.execute(
            config=config,
            params=Pagination(filters=[
                FilterManager(
                    field="email",
                    value=params.admin_user.email,
                    condition=CONDITION_TYPE.EQUALS
                )
            ])
        )
        if existing_users and not isinstance(existing_users, str):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CREATE_COMPANY_EMAIL_ALREADY_EXISTS.value
                ),
            )
        
        # Validar country existe
        country = await self.country_read_uc.execute(
            config=config,
            params=CountryRead(id=params.location.country_id)
        )
        if isinstance(country, str) or not country:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CREATE_COMPANY_COUNTRY_NOT_FOUND.value
                ),
            )
        
        # Validar language existe
        language = await self.language_read_uc.execute(
            config=config,
            params=LanguageRead(id=params.admin_user.language_id)
        )
        if isinstance(language, str) or not language:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CREATE_COMPANY_LANGUAGE_NOT_FOUND.value
                ),
            )
        
        # Validar currency existe
        currency = await self.currency_read_uc.execute(
            config=config,
            params=CurrencyRead(id=params.admin_user.currency_id)
        )
        if isinstance(currency, str) or not currency:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CREATE_COMPANY_CURRENCY_NOT_FOUND.value
                ),
            )
        
        # Validar rol existe
        rol = await self.rol_read_uc.execute(
            config=config,
            params=RolRead(id=params.admin_user.rol_id)
        )
        if isinstance(rol, str) or not rol:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CREATE_COMPANY_ROL_NOT_FOUND.value
                ),
            )
        
        # Validar que existan menús template (company_id = NULL)
        template_menus = await self.menu_list_uc.execute(
            config=config,
            params=Pagination(
                filters=[
                    FilterManager(
                        field="company_id",
                        value=None,
                        condition=CONDITION_TYPE.EQUALS
                    )
                ],
                all_data=True
            )
        )
        if not template_menus or isinstance(template_menus, str):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CREATE_COMPANY_NO_MENU_TEMPLATES.value
                ),
            )
        
        # ============================================
        # 2. CREAR COMPAÑÍA
        # ============================================
        
        company = await self.company_save_uc.execute(
            config=config,
            params=CompanySave(
                name=params.company.name,
                nit=params.company.nit,
                inactivity_time=params.company.inactivity_time,
                state=True
            )
        )
        
        if isinstance(company, str) or not company:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_ERROR_SAVING_RECORD.value
                ),
            )
        
        # ============================================
        # 3. CLONAR MENÚS MANTENIENDO JERARQUÍAS
        # ============================================
        
        # Usar caso de uso auxiliar para clonar menús
        clone_result = await self.clone_menus_uc.execute(
            config=config,
            company_id=company.id,
            template_menus=template_menus
        )
        
        if isinstance(clone_result, str):
            return clone_result  # Error en clonación
        
        cloned_menus, menu_mapping = clone_result
        
        # ============================================
        # 4. CLONAR PERMISOS DE MENÚS
        # ============================================
        
        # Usar caso de uso auxiliar para clonar permisos
        permissions_result = await self.clone_permissions_uc.execute(
            config=config,
            cloned_menus=cloned_menus,
            menu_mapping=menu_mapping
        )
        
        if isinstance(permissions_result, str):
            return permissions_result  # Error en clonación de permisos
        
        permissions_created = permissions_result
        
        # ============================================
        # 5. CREAR UBICACIÓN PRINCIPAL
        # ============================================
        
        location = await self.location_save_uc.execute(
            config=config,
            params=LocationSave(
                company_id=company.id,
                country_id=params.location.country_id,
                name=params.location.name,
                address=params.location.address,
                city=params.location.city,
                phone=params.location.phone,
                email=params.location.email,
                main_location=True,
                state=True
            )
        )
        
        if isinstance(location, str) or not location:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CREATE_COMPANY_ERROR_CREATING_LOCATION.value
                ),
            )
        
        # ============================================
        # 6. CREAR CURRENCY_LOCATION (asociar moneda a ubicación)
        # ============================================
        
        currency_location = await self.currency_location_save_uc.execute(
            config=config,
            params=CurrencyLocationSave(
                currency_id=params.admin_user.currency_id,
                location_id=location.id,
                state=True
            )
        )
        
        if isinstance(currency_location, str) or not currency_location:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CREATE_COMPANY_ERROR_CREATING_CURRENCY_LOCATION.value
                ),
            )
        
        # ============================================
        # 7. CREAR USUARIO ADMINISTRADOR INICIAL
        # ============================================
        
        user_result = await self.create_user_internal_uc.execute(
            config=config,
            params=CreateUserInternalRequest(
                language_id=params.admin_user.language_id,
                currency_id=params.admin_user.currency_id,
                location_rol=[
                    LocationRolItem(
                        location_id=location.id,
                        rol_id=params.admin_user.rol_id
                    )
                ],
                email=params.admin_user.email,
                password=params.admin_user.password,
                identification=params.admin_user.identification,
                first_name=params.admin_user.first_name,
                last_name=params.admin_user.last_name,
                phone=params.admin_user.phone
            )
        )
        
        if isinstance(user_result, str):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CREATE_COMPANY_ERROR_CREATING_ADMIN.value
                ),
            )
        
        # ============================================
        # 8. RETORNAR MENSAJE DE ÉXITO
        # ============================================
        
        return await self.message.get_message(
            config=config,
            message=MessageCoreEntity(
                key=KEYS_MESSAGES.CREATE_COMPANY_SUCCESS.value
            ),
        )


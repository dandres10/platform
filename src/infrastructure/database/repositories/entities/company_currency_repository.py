
from datetime import datetime
from typing import List, Optional, Union
from src.core.config import settings
from sqlalchemy.future import select
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.methods.get_filter import get_filter
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.company_currency.index import (
    CompanyCurrency,
    CompanyCurrencyDelete,
    CompanyCurrencyRead,
    CompanyCurrencyUpdate,
)
from src.domain.services.repositories.entities.i_company_currency_repository import (
    ICompanyCurrencyRepository,
)
from src.infrastructure.database.entities.company_currency_entity import CompanyCurrencyEntity
from src.infrastructure.database.mappers.company_currency_mapper import (
    map_to_company_currency,
    map_to_list_company_currency,
)


class CompanyCurrencyRepository(ICompanyCurrencyRepository):
    """Repository de company_currency.

    Patrón UoW (request-level transaction): este repo NO hace commit ni rollback.
    Usa db.flush() para empujar los statements a la sesión y refresh() para
    recargar los valores generados por el server (defaults, triggers). El
    commit/rollback final lo gestiona el orquestador del request.
    """

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def save(self, config: Config, params: CompanyCurrencyEntity) -> Union[CompanyCurrency, None]:
        db = config.async_db
        db.add(params)
        await db.flush()
        await db.refresh(params)
        return map_to_company_currency(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def update(self, config: Config, params: CompanyCurrencyUpdate) -> Union[CompanyCurrency, None]:
        db = config.async_db
        company_id = config.token.company_id if config.token else None

        stmt = select(CompanyCurrencyEntity).filter(CompanyCurrencyEntity.id == params.id)
        if company_id:
            stmt = stmt.filter(CompanyCurrencyEntity.company_id == company_id)

        result = await db.execute(stmt)
        company_currency = result.scalars().first()

        if not company_currency:
            return None

        update_data = params.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(company_currency, key, value)
        company_currency.updated_date = datetime.now()

        await db.flush()
        await db.refresh(company_currency)
        return map_to_company_currency(company_currency)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def list(self, config: Config, params: Pagination) -> Union[List[CompanyCurrency], None]:
        db = config.async_db
        company_id = config.token.company_id if config.token else None

        stmt = select(CompanyCurrencyEntity)

        # Multi-tenant filter (R9): siempre que haya company_id en el token,
        # restringir al tenant actual.
        if company_id:
            stmt = stmt.filter(CompanyCurrencyEntity.company_id == company_id)

        if params.filters:
            stmt = get_filter(
                query=stmt, filters=params.filters, entity=CompanyCurrencyEntity
            )

        if not params.all_data:
            stmt = stmt.offset(params.skip).limit(params.limit)

        result = await db.execute(stmt)
        company_currencies = result.scalars().all()

        if not company_currencies:
            return None
        return map_to_list_company_currency(company_currencies)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def delete(
        self,
        config: Config,
        params: CompanyCurrencyDelete,
    ) -> Union[CompanyCurrency, None]:
        db = config.async_db
        company_id = config.token.company_id if config.token else None

        stmt = select(CompanyCurrencyEntity).filter(CompanyCurrencyEntity.id == params.id)
        if company_id:
            stmt = stmt.filter(CompanyCurrencyEntity.company_id == company_id)

        result = await db.execute(stmt)
        company_currency = result.scalars().first()

        if not company_currency:
            return None

        snapshot = map_to_company_currency(company_currency)
        await db.delete(company_currency)
        await db.flush()
        return snapshot

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def read(
        self,
        config: Config,
        params: CompanyCurrencyRead,
    ) -> Union[CompanyCurrency, None]:
        db = config.async_db
        company_id = config.token.company_id if config.token else None

        stmt = select(CompanyCurrencyEntity).filter(CompanyCurrencyEntity.id == params.id)
        if company_id:
            stmt = stmt.filter(CompanyCurrencyEntity.company_id == company_id)

        result = await db.execute(stmt)
        company_currency = result.scalars().first()

        if not company_currency:
            return None

        return map_to_company_currency(company_currency)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def find_base_by_company(
        self,
        config: Config,
        company_id,
    ) -> Optional[CompanyCurrency]:
        """Devuelve la fila base (is_base=true) de la company indicada.

        Multi-tenant guard: si el token trae un company_id distinto al
        parámetro recibido, retornamos None para evitar leak cross-tenant.
        Si el token no trae company_id (usuario externo / system), confiamos
        en el caller. El UC `update` siempre debería pasar el company_id
        leído de la fila ya validada bajo el filtro multi-tenant del repo.
        """
        db = config.async_db
        token_company_id = config.token.company_id if config.token else None

        if token_company_id and str(token_company_id) != str(company_id):
            return None

        stmt = (
            select(CompanyCurrencyEntity)
            .filter(CompanyCurrencyEntity.company_id == company_id)
            .filter(CompanyCurrencyEntity.is_base == True)  # noqa: E712
            .limit(1)
        )

        result = await db.execute(stmt)
        company_currency = result.scalars().first()

        if not company_currency:
            return None

        return map_to_company_currency(company_currency)

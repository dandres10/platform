
from typing import List, Union
from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.methods.get_filter import get_filter
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.platform.index import (
    Platform,
    PlatformDelete,
    PlatformRead,
    PlatformUpdate,
)
from src.domain.services.repositories.entities.i_platform_repository import (
    IPlatformRepository,
)
from src.infrastructure.database.entities.platform_entity import PlatformEntity
from src.infrastructure.database.mappers.platform_mapper import (
    map_to_platform,
    map_to_list_platform,
)


class PlatformRepository(IPlatformRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def save(self, config: Config, params: PlatformEntity) -> Union[Platform, None]:
        db = config.db
        db.add(params)
        db.commit()
        db.refresh(params)
        return map_to_platform(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def update(self, config: Config, params: PlatformUpdate) -> Union[Platform, None]:
        db = config.db

        platform: PlatformEntity = (
            db.query(PlatformEntity).filter(PlatformEntity.id == params.id).first()
        )

        if not platform:
            return None

        update_data = params.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(platform, key, value)

        db.commit()
        db.refresh(platform)
        return map_to_platform(platform)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def list(self, config: Config, params: Pagination) -> Union[List[Platform], None]:
        db = config.db
        query = db.query(PlatformEntity)

        if params.all_data:
            if params.filters:
                query = get_filter(
                    query=query, filters=params.filters, entity=PlatformEntity
                )
                platforms = query.all()
            else:
                platforms = query.all()
        else:
            if params.filters:
                query = get_filter(
                    query=query, filters=params.filters, entity=PlatformEntity
                )
                platforms = query.offset(params.skip).limit(params.limit).all()

        if not platforms:
            return None
        return map_to_list_platform(platforms)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def delete(
        self,
        config: Config,
        params: PlatformDelete,
    ) -> Union[Platform, None]:
        db = config.db
        platform: PlatformEntity = (
            db.query(PlatformEntity).filter(PlatformEntity.id == params.id).first()
        )

        if not platform:
            return None

        db.delete(platform)
        db.commit()
        return map_to_platform(platform)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def read(
        self,
        config: Config,
        params: PlatformRead,
    ) -> Union[Platform, None]:
        db = config.db
        platform: PlatformEntity = (
            db.query(PlatformEntity).filter(PlatformEntity.id == params.id).first()
        )

        if not platform:
            return None

        return map_to_platform(platform)
        

from typing import List, Union
from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.methods.get_filter import get_filter
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.user_location.index import (
    UserLocation,
    UserLocationDelete,
    UserLocationRead,
    UserLocationUpdate,
)
from src.domain.services.repositories.entities.i_user_location_repository import (
    IUserLocationRepository,
)
from src.infrastructure.database.entities.user_location_entity import UserLocationEntity
from src.infrastructure.database.mappers.user_location_mapper import (
    map_to_user_location,
    map_to_list_user_location,
)


class UserLocationRepository(IUserLocationRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def save(self, config: Config, params: UserLocationEntity) -> Union[UserLocation, None]:
        db = config.db
        db.add(params)
        db.commit()
        db.refresh(params)
        return map_to_user_location(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def update(self, config: Config, params: UserLocationUpdate) -> Union[UserLocation, None]:
        db = config.db

        user_location: UserLocationEntity = (
            db.query(UserLocationEntity).filter(UserLocationEntity.id == params.id).first()
        )

        if not user_location:
            return None

        update_data = params.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user_location, key, value)

        db.commit()
        db.refresh(user_location)
        return map_to_user_location(user_location)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def list(self, config: Config, params: Pagination) -> Union[List[UserLocation], None]:
        db = config.db
        query = db.query(UserLocationEntity)

        if params.all_data:
            if params.filters:
                query = get_filter(
                    query=query, filters=params.filters, entity=UserLocationEntity
                )
                user_locations = query.all()
            else:
                user_locations = query.all()
        else:
            if params.filters:
                query = get_filter(
                    query=query, filters=params.filters, entity=UserLocationEntity
                )
                user_locations = query.offset(params.skip).limit(params.limit).all()

        if not user_locations:
            return None
        return map_to_list_user_location(user_locations)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def delete(
        self,
        config: Config,
        params: UserLocationDelete,
    ) -> Union[UserLocation, None]:
        db = config.db
        user_location: UserLocationEntity = (
            db.query(UserLocationEntity).filter(UserLocationEntity.id == params.id).first()
        )

        if not user_location:
            return None

        db.delete(user_location)
        db.commit()
        return map_to_user_location(user_location)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def read(
        self,
        config: Config,
        params: UserLocationRead,
    ) -> Union[UserLocation, None]:
        db = config.db
        user_location: UserLocationEntity = (
            db.query(UserLocationEntity).filter(UserLocationEntity.id == params.id).first()
        )

        if not user_location:
            return None

        return map_to_user_location(user_location)
        

from typing import List, Union
from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.methods.get_filter import get_filter
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.location.index import (
    Location,
    LocationDelete,
    LocationRead,
    LocationUpdate,
)
from src.domain.services.repositories.entities.i_location_repository import (
    ILocationRepository,
)
from src.infrastructure.database.entities.location_entity import LocationEntity
from src.infrastructure.database.mappers.location_mapper import (
    map_to_location,
    map_to_list_location,
)


class LocationRepository(ILocationRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def save(self, config: Config, params: LocationEntity) -> Union[Location, None]:
        db = config.db
        db.add(params)
        db.commit()
        db.refresh(params)
        return map_to_location(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def update(self, config: Config, params: LocationUpdate) -> Union[Location, None]:
        db = config.db

        location: LocationEntity = (
            db.query(LocationEntity).filter(LocationEntity.id == params.id).first()
        )

        if not location:
            return None

        update_data = params.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(location, key, value)

        db.commit()
        db.refresh(location)
        return map_to_location(location)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def list(self, config: Config, params: Pagination) -> Union[List[Location], None]:
        db = config.db
        query = db.query(LocationEntity)

        if params.all_data:
            locations = query.all()
        else:
            if params.filters:
                query = get_filter(
                    query=query, filters=params.filters, entity=LocationEntity
                )
                locations = query.offset(params.skip).limit(params.limit).all()

        if not locations:
            return None
        return map_to_list_location(locations)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def delete(
        self,
        config: Config,
        params: LocationDelete,
    ) -> Union[Location, None]:
        db = config.db
        location: LocationEntity = (
            db.query(LocationEntity).filter(LocationEntity.id == params.id).first()
        )

        if not location:
            return None

        db.delete(location)
        db.commit()
        return map_to_location(location)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def read(
        self,
        config: Config,
        params: LocationRead,
    ) -> Union[Location, None]:
        db = config.db
        location: LocationEntity = (
            db.query(LocationEntity).filter(LocationEntity.id == params.id).first()
        )

        if not location:
            return None

        return map_to_location(location)
        
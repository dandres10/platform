
from typing import List, Union
from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.methods.get_filter import get_filter
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.user_location_rol.index import (
    UserLocationRol,
    UserLocationRolDelete,
    UserLocationRolRead,
    UserLocationRolUpdate,
)
from src.domain.services.repositories.entities.i_user_location_rol_repository import (
    IUserLocationRolRepository,
)
from src.infrastructure.database.entities.user_location_rol_entity import UserLocationRolEntity
from src.infrastructure.database.mappers.user_location_rol_mapper import (
    map_to_user_location_rol,
    map_to_list_user_location_rol,
)


class UserLocationRolRepository(IUserLocationRolRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def save(self, config: Config, params: UserLocationRolEntity) -> Union[UserLocationRol, None]:
        db = config.db
        db.add(params)
        db.commit()
        db.refresh(params)
        return map_to_user_location_rol(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def update(self, config: Config, params: UserLocationRolUpdate) -> Union[UserLocationRol, None]:
        db = config.db

        user_location_rol: UserLocationRolEntity = (
            db.query(UserLocationRolEntity).filter(UserLocationRolEntity.id == params.id).first()
        )

        if not user_location_rol:
            return None

        update_data = params.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user_location_rol, key, value)

        db.commit()
        db.refresh(user_location_rol)
        return map_to_user_location_rol(user_location_rol)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def list(self, config: Config, params: Pagination) -> Union[List[UserLocationRol], None]:
        db = config.db
        query = db.query(UserLocationRolEntity)

        if params.all_data:
            if params.filters:
                query = get_filter(
                    query=query, filters=params.filters, entity=UserLocationRolEntity
                )
                user_location_rols = query.all()
            else:
                user_location_rols = query.all()
        else:
            if params.filters:
                query = get_filter(
                    query=query, filters=params.filters, entity=UserLocationRolEntity
                )
                user_location_rols = query.offset(params.skip).limit(params.limit).all()

        if not user_location_rols:
            return None
        return map_to_list_user_location_rol(user_location_rols)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def delete(
        self,
        config: Config,
        params: UserLocationRolDelete,
    ) -> Union[UserLocationRol, None]:
        db = config.db
        user_location_rol: UserLocationRolEntity = (
            db.query(UserLocationRolEntity).filter(UserLocationRolEntity.id == params.id).first()
        )

        if not user_location_rol:
            return None

        db.delete(user_location_rol)
        db.commit()
        return map_to_user_location_rol(user_location_rol)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def read(
        self,
        config: Config,
        params: UserLocationRolRead,
    ) -> Union[UserLocationRol, None]:
        db = config.db
        user_location_rol: UserLocationRolEntity = (
            db.query(UserLocationRolEntity).filter(UserLocationRolEntity.id == params.id).first()
        )

        if not user_location_rol:
            return None

        return map_to_user_location_rol(user_location_rol)
        
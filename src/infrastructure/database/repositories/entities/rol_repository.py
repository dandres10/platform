
from typing import List, Union
from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.methods.get_filter import get_filter
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.rol.index import (
    Rol,
    RolDelete,
    RolRead,
    RolUpdate,
)
from src.domain.services.repositories.entities.i_rol_repository import (
    IRolRepository,
)
from src.infrastructure.database.entities.rol_entity import RolEntity
from src.infrastructure.database.mappers.rol_mapper import (
    map_to_rol,
    map_to_list_rol,
)


class RolRepository(IRolRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def save(self, config: Config, params: RolEntity) -> Union[Rol, None]:
        db = config.db
        db.add(params)
        db.commit()
        db.refresh(params)
        return map_to_rol(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def update(self, config: Config, params: RolUpdate) -> Union[Rol, None]:
        db = config.db

        rol: RolEntity = (
            db.query(RolEntity).filter(RolEntity.id == params.id).first()
        )

        if not rol:
            return None

        update_data = params.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(rol, key, value)

        db.commit()
        db.refresh(rol)
        return map_to_rol(rol)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def list(self, config: Config, params: Pagination) -> Union[List[Rol], None]:
        db = config.db
        query = db.query(RolEntity)

        if params.all_data:
            if params.filters:
                query = get_filter(
                    query=query, filters=params.filters, entity=RolEntity
                )
                rols = query.all()
            else:
                rols = query.all()
        else:
            if params.filters:
                query = get_filter(
                    query=query, filters=params.filters, entity=RolEntity
                )
                rols = query.offset(params.skip).limit(params.limit).all()

        if not rols:
            return None
        return map_to_list_rol(rols)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def delete(
        self,
        config: Config,
        params: RolDelete,
    ) -> Union[Rol, None]:
        db = config.db
        rol: RolEntity = (
            db.query(RolEntity).filter(RolEntity.id == params.id).first()
        )

        if not rol:
            return None

        db.delete(rol)
        db.commit()
        return map_to_rol(rol)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def read(
        self,
        config: Config,
        params: RolRead,
    ) -> Union[Rol, None]:
        db = config.db
        rol: RolEntity = (
            db.query(RolEntity).filter(RolEntity.id == params.id).first()
        )

        if not rol:
            return None

        return map_to_rol(rol)
        
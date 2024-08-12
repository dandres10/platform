
from typing import List, Union
from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.methods.get_filter import get_filter
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.permission.index import (
    Permission,
    PermissionDelete,
    PermissionRead,
    PermissionUpdate,
)
from src.domain.services.repositories.entities.i_permission_repository import (
    IPermissionRepository,
)
from src.infrastructure.database.entities.permission_entity import PermissionEntity
from src.infrastructure.database.mappers.permission_mapper import (
    map_to_permission,
    map_to_list_permission,
)


class PermissionRepository(IPermissionRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def save(self, config: Config, params: PermissionEntity) -> Union[Permission, None]:
        db = config.db
        db.add(params)
        db.commit()
        db.refresh(params)
        return map_to_permission(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def update(self, config: Config, params: PermissionUpdate) -> Union[Permission, None]:
        db = config.db

        permission: PermissionEntity = (
            db.query(PermissionEntity).filter(PermissionEntity.id == params.id).first()
        )

        if not permission:
            return None

        update_data = params.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(permission, key, value)

        db.commit()
        db.refresh(permission)
        return map_to_permission(permission)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def list(self, config: Config, params: Pagination) -> Union[List[Permission], None]:
        db = config.db
        query = db.query(PermissionEntity)

        if params.all_data:
            permissions = query.all()
        else:
            if params.filters:
                query = get_filter(
                    query=query, filters=params.filters, entity=PermissionEntity
                )
                permissions = query.offset(params.skip).limit(params.limit).all()

        if not permissions:
            return None
        return map_to_list_permission(permissions)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def delete(
        self,
        config: Config,
        params: PermissionDelete,
    ) -> Union[Permission, None]:
        db = config.db
        permission: PermissionEntity = (
            db.query(PermissionEntity).filter(PermissionEntity.id == params.id).first()
        )

        if not permission:
            return None

        db.delete(permission)
        db.commit()
        return map_to_permission(permission)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def read(
        self,
        config: Config,
        params: PermissionRead,
    ) -> Union[Permission, None]:
        db = config.db
        permission: PermissionEntity = (
            db.query(PermissionEntity).filter(PermissionEntity.id == params.id).first()
        )

        if not permission:
            return None

        return map_to_permission(permission)
        
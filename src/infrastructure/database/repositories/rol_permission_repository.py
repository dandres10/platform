
from typing import List, Union
from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.methods.get_filter import get_filter
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.rol_permission.index import (
    RolPermission,
    RolPermissionDelete,
    RolPermissionRead,
    RolPermissionUpdate,
)
from src.domain.services.repositories.entities.i_rol_permission_repository import (
    IRolPermissionRepository,
)
from src.infrastructure.database.entities.rol_permission_entity import RolPermissionEntity
from src.infrastructure.database.mappers.rol_permission_mapper import (
    map_to_rol_permission,
    map_to_list_rol_permission,
)


class RolPermissionRepository(IRolPermissionRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def save(self, config: Config, params: RolPermissionEntity) -> Union[RolPermission, None]:
        db = config.db
        db.add(params)
        db.commit()
        db.refresh(params)
        return map_to_rol_permission(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def update(self, config: Config, params: RolPermissionUpdate) -> Union[RolPermission, None]:
        db = config.db

        rol_permission: RolPermissionEntity = (
            db.query(RolPermissionEntity).filter(RolPermissionEntity.id == params.id).first()
        )

        if not rol_permission:
            return None

        update_data = params.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(rol_permission, key, value)

        db.commit()
        db.refresh(rol_permission)
        return map_to_rol_permission(rol_permission)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def list(self, config: Config, params: Pagination) -> Union[List[RolPermission], None]:
        db = config.db
        query = db.query(RolPermissionEntity)

        if params.all_data:
            rol_permissions = query.all()
        else:
            if params.filters:
                query = get_filter(
                    query=query, filters=params.filters, entity=RolPermissionEntity
                )
                rol_permissions = query.offset(params.skip).limit(params.limit).all()

        if not rol_permissions:
            return None
        return map_to_list_rol_permission(rol_permissions)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def delete(
        self,
        config: Config,
        params: RolPermissionDelete,
    ) -> Union[RolPermission, None]:
        db = config.db
        rol_permission: RolPermissionEntity = (
            db.query(RolPermissionEntity).filter(RolPermissionEntity.id == params.id).first()
        )

        if not rol_permission:
            return None

        db.delete(rol_permission)
        db.commit()
        return map_to_rol_permission(rol_permission)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def read(
        self,
        config: Config,
        params: RolPermissionRead,
    ) -> Union[RolPermission, None]:
        db = config.db
        rol_permission: RolPermissionEntity = (
            db.query(RolPermissionEntity).filter(RolPermissionEntity.id == params.id).first()
        )

        if not rol_permission:
            return None

        return map_to_rol_permission(rol_permission)
        
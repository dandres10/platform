
from typing import List, Union
from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.methods.get_filter import get_filter
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.user.index import (
    User,
    UserDelete,
    UserRead,
    UserUpdate,
)
from src.domain.services.repositories.entities.i_user_repository import (
    IUserRepository,
)
from src.infrastructure.database.entities.user_entity import UserEntity
from src.infrastructure.database.mappers.user_mapper import (
    map_to_user,
    map_to_list_user,
)


class UserRepository(IUserRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def save(self, config: Config, params: UserEntity) -> Union[User, None]:
        db = config.db
        db.add(params)
        db.commit()
        db.refresh(params)
        return map_to_user(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def update(self, config: Config, params: UserUpdate) -> Union[User, None]:
        db = config.db

        user: UserEntity = (
            db.query(UserEntity).filter(UserEntity.id == params.id).first()
        )

        if not user:
            return None

        update_data = params.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        db.commit()
        db.refresh(user)
        return map_to_user(user)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def list(self, config: Config, params: Pagination) -> Union[List[User], None]:
        db = config.db
        query = db.query(UserEntity)

        if params.all_data:
            if params.filters:
                query = get_filter(
                    query=query, filters=params.filters, entity=UserEntity
                )
                users = query.all()
            else:
                users = query.all()
        else:
            if params.filters:
                query = get_filter(
                    query=query, filters=params.filters, entity=UserEntity
                )
                users = query.offset(params.skip).limit(params.limit).all()

        if not users:
            return None
        return map_to_list_user(users)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def delete(
        self,
        config: Config,
        params: UserDelete,
    ) -> Union[User, None]:
        db = config.db
        user: UserEntity = (
            db.query(UserEntity).filter(UserEntity.id == params.id).first()
        )

        if not user:
            return None

        db.delete(user)
        db.commit()
        return map_to_user(user)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def read(
        self,
        config: Config,
        params: UserRead,
    ) -> Union[User, None]:
        db = config.db
        user: UserEntity = (
            db.query(UserEntity).filter(UserEntity.id == params.id).first()
        )

        if not user:
            return None

        return map_to_user(user)
        
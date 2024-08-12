
from typing import List
from src.domain.models.entities.rol.index import (
    Rol,
    RolSave,
    RolUpdate,
)
from src.infrastructure.database.entities.rol_entity import RolEntity


def map_to_rol(rol_entity: RolEntity) -> Rol:
    return Rol(
        id=rol_entity.id,
        company_id=rol_entity.company_id,
        name=rol_entity.name,
        code=rol_entity.code,
        description=rol_entity.description,
        state=rol_entity.state,
        created_date=rol_entity.created_date,
        updated_date=rol_entity.updated_date,
    )

def map_to_list_rol(rol_entities: List[RolEntity]) -> List[Rol]:
    return [map_to_rol(rol) for rol in rol_entities]

def map_to_rol_entity(rol: Rol) -> RolEntity:
    return RolEntity(
        id=rol.id,
        company_id=rol.company_id,
        name=rol.name,
        code=rol.code,
        description=rol.description,
        state=rol.state,
        created_date=rol.created_date,
        updated_date=rol.updated_date,
    )

def map_to_list_rol_entity(rols: List[Rol]) -> List[RolEntity]:
    return [map_to_rol_entity(rol) for rol in rols]

def map_to_save_rol_entity(rol: RolSave) -> RolEntity:
    return RolEntity(
        company_id=rol.company_id,
        name=rol.name,
        code=rol.code,
        description=rol.description,
        state=rol.state,
    )

def map_to_update_rol_entity(rol: RolUpdate) -> RolEntity:
    return RolEntity(
        id=rol.id,
        company_id=rol.company_id,
        name=rol.name,
        code=rol.code,
        description=rol.description,
        state=rol.state,
    )


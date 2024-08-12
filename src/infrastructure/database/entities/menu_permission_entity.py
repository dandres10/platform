from sqlalchemy.sql import func
from src.core.models.base import Base
from sqlalchemy import Column, String, Boolean, DateTime, text, Text, Integer, Float
from sqlalchemy.dialects.postgresql import UUID

class MenuPermissionEntity(Base):
    __tablename__ = 'menu_permission'

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text('uuid_generate_v4()'))
    menu_id = Column(UUID(as_uuid=True), nullable=True)
    permission_id = Column(UUID(as_uuid=True), nullable=True)
    state = Column(Boolean, nullable=False, server_default=text('true'))
    created_date = Column(DateTime, nullable=False, server_default=text('now()'))
    updated_date = Column(DateTime, nullable=False, server_default=text('now()'), onupdate=text('now()'))

from sqlalchemy.sql import func
from src.core.config import settings
from src.core.models.base import Base
from sqlalchemy import Column, String, Boolean, DateTime, text, Text, Integer, Float, Time, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

class UserLocationRolEntity(Base):
    __tablename__ = 'user_location_rol'
    __table_args__ = {"schema": settings.database_schema}

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text('uuid_generate_v4()'))
    user_id = Column(UUID(as_uuid=True), ForeignKey(f'{settings.database_schema}.user.id'), nullable=False)
    location_id = Column(UUID(as_uuid=True), ForeignKey(f'{settings.database_schema}.location.id'), nullable=True)
    rol_id = Column(UUID(as_uuid=True), ForeignKey(f'{settings.database_schema}.rol.id'), nullable=False)
    state = Column(Boolean, nullable=False, server_default=text('true'))
    created_date = Column(DateTime(timezone=True), nullable=False, server_default=text('now()'))
    updated_date = Column(DateTime(timezone=True), nullable=False, server_default=text('now()'), onupdate=text('now()'))

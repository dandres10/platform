from sqlalchemy.sql import func
from src.core.models.base import Base
from sqlalchemy import Column, String, Boolean, DateTime, text, Text, Integer, Float
from sqlalchemy.dialects.postgresql import UUID

class PlatformEntity(Base):
    __tablename__ = 'platform'

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text('uuid_generate_v4()'))
    language_id = Column(UUID(as_uuid=True), nullable=True)
    location_id = Column(UUID(as_uuid=True), nullable=True)
    currency_location_id = Column(UUID(as_uuid=True), nullable=True)
    token_expiration_minutes = Column(Integer, nullable=False, server_default=text('60'))
    refresh_token_expiration_minutes = Column(Integer, nullable=False, server_default=text('62'))
    created_date = Column(DateTime, nullable=False, server_default=text('now()'))
    updated_date = Column(DateTime, nullable=False, server_default=text('now()'), onupdate=text('now()'))

from sqlalchemy.sql import func
from src.core.config import settings
from src.core.models.base import Base
from sqlalchemy import Column, String, Boolean, DateTime, text, Text, Integer, Float, Time, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

class PlatformEntity(Base):
    __tablename__ = 'platform'
    __table_args__ = {"schema": settings.database_schema}

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text('uuid_generate_v4()'))
    language_id = Column(UUID(as_uuid=True), ForeignKey(f'{settings.database_schema}.language.id'), nullable=False)
    location_id = Column(UUID(as_uuid=True), ForeignKey(f'{settings.database_schema}.location.id'), nullable=True)
    currency_id = Column(UUID(as_uuid=True), ForeignKey(f'{settings.database_schema}.currency.id'), nullable=False)
    token_expiration_minutes = Column(Integer, nullable=False, server_default=text('60'))
    refresh_token_expiration_minutes = Column(Integer, nullable=False, server_default=text('62'))
    created_date = Column(DateTime, nullable=False, server_default=text('now()'))
    updated_date = Column(DateTime, nullable=False, server_default=text('now()'), onupdate=text('now()'))

from sqlalchemy.sql import func
from src.core.config import settings
from src.core.models.base import Base
from sqlalchemy import Column, String, Boolean, DateTime, text, Text, Integer, Float, Time
from sqlalchemy.dialects.postgresql import UUID

class UserCountryEntity(Base):
    __tablename__ = 'user_country'
    __table_args__ = {"schema": settings.database_schema}

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text('uuid_generate_v4()'))
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    country_id = Column(UUID(as_uuid=True), nullable=False)  # FK a geo_division(id) - nodo tipo COUNTRY
    state = Column(Boolean, nullable=False, server_default=text('true'))
    created_date = Column(DateTime, nullable=False, server_default=text('now()'))
    updated_date = Column(DateTime, nullable=False, server_default=text('now()'), onupdate=text('now()'))

from sqlalchemy.sql import func
from src.core.config import settings
from src.core.models.base import Base
from sqlalchemy import Column, String, Boolean, DateTime, text, Text, Integer, Float, Time
from sqlalchemy.dialects.postgresql import UUID

class CompanyCurrencyEntity(Base):
    __tablename__ = 'company_currency'
    __table_args__ = {"schema": settings.database_schema}

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text('uuid_generate_v4()'))
    company_id = Column(UUID(as_uuid=True), nullable=False)
    currency_id = Column(UUID(as_uuid=True), nullable=False)
    is_base = Column(Boolean, nullable=False, server_default=text('false'))
    state = Column(Boolean, nullable=False, server_default=text('true'))
    created_date = Column(DateTime(timezone=True), nullable=False, server_default=text('now()'))
    updated_date = Column(DateTime(timezone=True), nullable=False, server_default=text('now()'), onupdate=text('now()'))

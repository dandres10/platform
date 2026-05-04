from sqlalchemy.sql import func
from src.core.config import settings
from src.core.models.base import Base
from sqlalchemy import Column, String, Boolean, DateTime, text, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

class GeoDivisionEntity(Base):
    __tablename__ = 'geo_division'
    __table_args__ = {"schema": settings.database_schema}

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text('uuid_generate_v4()'))
    top_id = Column(UUID(as_uuid=True), ForeignKey(f'{settings.database_schema}.geo_division.id'), nullable=True)
    geo_division_type_id = Column(UUID(as_uuid=True), ForeignKey(f'{settings.database_schema}.geo_division_type.id'), nullable=False)
    name = Column(String(255), nullable=False)
    code = Column(String(20), nullable=True)
    phone_code = Column(String(10), nullable=True)
    level = Column(Integer, nullable=False, server_default=text('0'))
    state = Column(Boolean, nullable=False, server_default=text('true'))
    created_date = Column(DateTime, nullable=False, server_default=text('now()'))
    updated_date = Column(DateTime, nullable=False, server_default=text('now()'), onupdate=text('now()'))

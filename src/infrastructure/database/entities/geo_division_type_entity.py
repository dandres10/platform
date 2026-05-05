from sqlalchemy.sql import func
from src.core.config import settings
from src.core.models.base import Base
from sqlalchemy import Column, String, Boolean, DateTime, text, Text
from sqlalchemy.dialects.postgresql import UUID

class GeoDivisionTypeEntity(Base):
    __tablename__ = 'geo_division_type'
    __table_args__ = {"schema": settings.database_schema}

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text('uuid_generate_v4()'))
    name = Column(String(50), nullable=False, unique=True)
    label = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    state = Column(Boolean, nullable=False, server_default=text('true'))
    created_date = Column(DateTime(timezone=True), nullable=False, server_default=text('now()'))
    updated_date = Column(DateTime(timezone=True), nullable=False, server_default=text('now()'), onupdate=text('now()'))

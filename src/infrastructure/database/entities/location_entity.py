from sqlalchemy.sql import func
from src.core.config import settings
from src.core.models.base import Base
from sqlalchemy import Column, String, Boolean, DateTime, text, Text, Integer, Float, Time
from sqlalchemy.dialects.postgresql import UUID

class LocationEntity(Base):
    __tablename__ = 'location'
    __table_args__ = {"schema": settings.database_schema}

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text('uuid_generate_v4()'))
    company_id = Column(UUID(as_uuid=True), nullable=True)
    country_id = Column(UUID(as_uuid=True), nullable=True)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    main_location = Column(Boolean, nullable=False, server_default=text('false'))
    state = Column(Boolean, nullable=False, server_default=text('true'))
    created_date = Column(DateTime, nullable=False, server_default=text('now()'))
    updated_date = Column(DateTime, nullable=False, server_default=text('now()'), onupdate=text('now()'))

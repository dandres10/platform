from sqlalchemy.sql import func
from src.core.config import settings
from src.core.models.base import Base
from sqlalchemy import Column, String, Boolean, DateTime, text, Text, Integer, Float, Time
from sqlalchemy.dialects.postgresql import UUID

class CompanyEntity(Base):
    __tablename__ = 'company'
    __table_args__ = {"schema": settings.database_schema}

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text('uuid_generate_v4()'))
    name = Column(String(255), nullable=False)
    inactivity_time = Column(Integer, nullable=False, server_default=text('20'))
    nit = Column(String(255), nullable=False)
    state = Column(Boolean, nullable=False, server_default=text('true'))
    created_date = Column(DateTime, nullable=False, server_default=text('now()'))
    updated_date = Column(DateTime, nullable=False, server_default=text('now()'), onupdate=text('now()'))

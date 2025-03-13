from sqlalchemy.sql import func
from src.core.config import settings
from src.core.models.base import Base
from sqlalchemy import Column, String, Boolean, DateTime, text, Text, Integer, Float, Time
from sqlalchemy.dialects.postgresql import UUID

class MenuEntity(Base):
    __tablename__ = 'menu'
    __table_args__ = {"schema": settings.database_schema}

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text('uuid_generate_v4()'))
    company_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String(100), nullable=False)
    label = Column(String(300), nullable=False)
    description = Column(String(300), nullable=False)
    top_id = Column(UUID(as_uuid=True), nullable=False)
    route = Column(String(300), nullable=False)
    state = Column(Boolean, nullable=False, server_default=text('true'))
    icon = Column(String(50), nullable=False)
    created_date = Column(DateTime, nullable=False, server_default=text('now()'))
    updated_date = Column(DateTime, nullable=False, server_default=text('now()'), onupdate=text('now()'))

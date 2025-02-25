from sqlalchemy.sql import func
from src.core.models.base import Base
from sqlalchemy import Column, String, Boolean, DateTime, text, Text, Integer, Float
from sqlalchemy.dialects.postgresql import UUID

class PermissionEntity(Base):
    __tablename__ = 'permission'

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text('uuid_generate_v4()'))
    company_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    state = Column(Boolean, nullable=False, server_default=text('true'))
    created_date = Column(DateTime, nullable=False, server_default=text('now()'))
    updated_date = Column(DateTime, nullable=False, server_default=text('now()'), onupdate=text('now()'))

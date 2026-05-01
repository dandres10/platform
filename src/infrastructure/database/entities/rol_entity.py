from sqlalchemy.sql import func
from src.core.config import settings
from src.core.models.base import Base
from sqlalchemy import Column, String, Boolean, DateTime, text, Text, Integer, Float, Time, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

class RolEntity(Base):
    __tablename__ = 'rol'
    __table_args__ = (
        UniqueConstraint('company_id', 'code', name='idx_rol_company_code'),
        {"schema": settings.database_schema},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text('uuid_generate_v4()'))
    company_id = Column(UUID(as_uuid=True), ForeignKey('company.id'), nullable=True)
    name = Column(String(255), nullable=False)
    code = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    state = Column(Boolean, nullable=False, server_default=text('true'))
    created_date = Column(DateTime, nullable=False, server_default=text('now()'))
    updated_date = Column(DateTime, nullable=False, server_default=text('now()'), onupdate=text('now()'))

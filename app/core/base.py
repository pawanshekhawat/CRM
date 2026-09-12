import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import DeclarativeBase, declared_attr

def generate_uuid() -> str:
    return str(uuid.uuid4())

def get_utc_now():
    return datetime.now(timezone.utc)

class Base(DeclarativeBase):
    """Base model for all database entities."""
    pass

class TimestampMixin:
    """Provides id, created_at, and updated_at fields for all models."""
    
    @declared_attr
    def id(cls):
        return Column(String(36), primary_key=True, default=generate_uuid)

    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=get_utc_now, nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)


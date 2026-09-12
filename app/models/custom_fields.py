import json
from typing import List, Optional
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.base import Base, TimestampMixin

class CustomFieldDefinition(Base, TimestampMixin):
    """Defines custom, user-configurable fields for any entity (e.g. Student, Staff, etc.)."""
    __tablename__ = "custom_field_definitions"

    entity_type = Column(String(50), nullable=False, index=True, default="student")
    field_name = Column(String(100), nullable=False) # e.g. "blood_group"
    field_label = Column(String(150), nullable=False) # e.g. "Blood Group"
    field_type = Column(String(50), nullable=False, default="text") # text, number, date, select, checkbox, textarea
    options_json = Column(Text, nullable=True) # JSON array of dropdown options for 'select'
    is_required = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)

    # Relationships
    values = relationship("CustomFieldValue", back_populates="definition", cascade="all, delete-orphan")

    def get_options(self) -> List[str]:
        if self.options_json:
            try:
                return json.loads(self.options_json)
            except Exception:
                return []
        return []

    def set_options(self, options: List[str]):
        self.options_json = json.dumps(options)

class CustomFieldValue(Base, TimestampMixin):
    """Stores the specific value of a custom field for an entity instance."""
    __tablename__ = "custom_field_values"

    entity_id = Column(String(36), nullable=False, index=True)
    field_id = Column(String(36), ForeignKey("custom_field_definitions.id", ondelete="CASCADE"), nullable=False, index=True)
    value_text = Column(Text, nullable=True)

    # Relationships
    definition = relationship("CustomFieldDefinition", back_populates="values")

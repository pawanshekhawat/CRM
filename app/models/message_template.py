from sqlalchemy import Boolean, Column, Integer, String, Text
from app.core.base import Base, TimestampMixin

class MessageTemplate(Base, TimestampMixin):
    """Stores reusable WhatsApp message templates and workflow scripts."""
    __tablename__ = "message_templates"

    title = Column(String(150), nullable=False) # e.g. "Fee Reminder (Outstanding Balance)"
    category = Column(String(100), default="Fees") # Fees, Admissions, Batches, General
    content = Column(Text, nullable=False) # Text with {name}, {balance_due}, Spintax {Dear|Hello}
    is_default = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)

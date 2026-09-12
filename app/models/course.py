from sqlalchemy import Column, Float, String, Text
from app.core.base import Base, TimestampMixin

class Course(Base, TimestampMixin):
    """Course program catalog entity with standard pricing and syllabus."""
    __tablename__ = "courses"

    course_code = Column(String(50), unique=True, nullable=False, index=True) # e.g. CRS-ARCH-01
    name = Column(String(150), unique=True, nullable=False, index=True) # e.g. Master Architecture
    category = Column(String(100), nullable=True, index=True) # e.g. Architecture & Civil, IT & Programming
    standard_fee = Column(Float, default=0.0, nullable=False) # e.g. 120000.0
    duration = Column(String(50), nullable=True) # Retained nullable in DB for schema compatibility
    description = Column(Text, nullable=True) # Syllabus / Tools Covered / Summary
    status = Column(String(50), default="Active", index=True) # Active, Inactive, Archived

    @property
    def formatted_fee(self) -> str:
        return f"₹{self.standard_fee:,.2f}"

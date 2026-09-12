from datetime import date
from sqlalchemy import (
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.base import Base, TimestampMixin

class Staff(Base, TimestampMixin):
    """Staff member / Faculty / Instructor / Management entity."""
    __tablename__ = "staff"

    staff_id = Column(String(50), unique=True, nullable=False, index=True) # e.g. STF-001
    name = Column(String(150), nullable=False, index=True)
    designation = Column(String(100), nullable=True) # e.g. Receptionist, Senior CAD Faculty
    department = Column(String(100), nullable=True) # e.g. Civil / Architecture, Admin
    mobile_no = Column(String(20), nullable=True, index=True)
    email = Column(String(120), nullable=True)
    qualification = Column(String(200), nullable=True) # e.g. B.Tech (Civil), M.Arch
    joining_date = Column(Date, default=date.today, nullable=True)
    salary = Column(Float, default=0.0)
    status = Column(String(50), default="Active", index=True) # Active, On Leave, Inactive, Resigned
    photo_path = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    batches = relationship(
        "Batch",
        back_populates="instructor",
        cascade="all, delete-orphan",
        order_by="Batch.batch_name",
    )

    assigned_students = relationship(
        "Student",
        back_populates="assigned_staff",
    )

    @property
    def active_batches_count(self) -> int:
        return sum(1 for b in (self.batches or []) if b.status == "Active")

    @property
    def total_students_count(self) -> int:
        """Count of distinct students enrolled in this staff's active batches or directly mentored."""
        direct_students = {s.id for s in (self.assigned_students or [])}
        batch_students = set()
        for b in (self.batches or []):
            for enr in (b.enrollments or []):
                if enr.status == "Active":
                    batch_students.add(enr.student_id)
        return len(direct_students.union(batch_students))


class Batch(Base, TimestampMixin):
    """Batch schedule grouping students under an assigned instructor."""
    __tablename__ = "batches"

    batch_code = Column(String(50), unique=True, nullable=False, index=True) # e.g. ARCH-M-01
    batch_name = Column(String(150), nullable=False, index=True) # e.g. Morning Architecture Master 9AM
    course_name = Column(String(200), nullable=True, index=True) # e.g. Master in Architecture
    staff_id = Column(String(36), ForeignKey("staff.id", ondelete="SET NULL"), nullable=True, index=True)
    
    start_time = Column(String(50), nullable=True, default="09:00 AM")
    end_time = Column(String(50), nullable=True, default="11:00 AM")
    days_schedule = Column(String(100), nullable=True, default="Mon-Fri") # Mon-Fri, Mon-Sat, Sat-Sun
    room_lab = Column(String(100), nullable=True, default="Lab 1 (CAD Station)")
    start_date = Column(Date, default=date.today, nullable=True)
    end_date = Column(Date, nullable=True)
    max_capacity = Column(Integer, default=20)
    status = Column(String(50), default="Active", index=True) # Active, Upcoming, Completed, Suspended
    remarks = Column(Text, nullable=True)

    # Relationships
    instructor = relationship("Staff", back_populates="batches")

    enrollments = relationship(
        "BatchStudent",
        back_populates="batch",
        cascade="all, delete-orphan",
        order_by="BatchStudent.enrolled_date",
    )

    students = relationship(
        "Student",
        secondary="batch_students",
        viewonly=True,
    )

    @property
    def enrolled_count(self) -> int:
        return sum(1 for e in (self.enrollments or []) if e.status == "Active")

    @property
    def instructor_name(self) -> str:
        return self.instructor.name if self.instructor else "Unassigned"


class BatchStudent(Base, TimestampMixin):
    """Student enrollment record inside a specific batch."""
    __tablename__ = "batch_students"

    batch_id = Column(String(36), ForeignKey("batches.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    enrolled_date = Column(Date, default=date.today, nullable=False)
    status = Column(String(50), default="Active", index=True) # Active, Completed, Dropped, Transferred
    remarks = Column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint("batch_id", "student_id", name="uq_batch_student"),
    )

    # Relationships
    batch = relationship("Batch", back_populates="enrollments")
    student = relationship("Student", back_populates="batch_enrollments")

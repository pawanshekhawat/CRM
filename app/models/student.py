from datetime import date
from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.base import Base, TimestampMixin

class Student(Base, TimestampMixin):
    """Core Student model representing admissions from CADDESK Centre form."""
    __tablename__ = "students"

    # Header / Identity
    id_no = Column(String(50), unique=True, nullable=False, index=True) # ID No.
    is_online = Column(Boolean, default=False) # Online admission checkbox
    online_reg_no = Column(String(100), nullable=True) # Online registration ID/portal ref
    photo_path = Column(String(255), nullable=True) # Relative path to passport photo
    admission_form_path = Column(String(255), nullable=True) # Relative path to scanned admission form image

    # Personal Information
    name = Column(String(150), nullable=False, index=True) # NAME
    father_name = Column(String(150), nullable=True) # Father's Name
    mother_name = Column(String(150), nullable=True) # Mother's Name
    dob = Column(Date, nullable=True) # D.O.B.
    father_occupation = Column(String(150), nullable=True) # Father's Occupation
    college_school = Column(String(200), nullable=True) # College/School
    course_name = Column(String(200), nullable=True, index=True) # Primary Course Name
    year_sem = Column(String(50), nullable=True) # Year/Sem.
    aadhar_no = Column(String(50), nullable=True, index=True) # Aadhar No.

    # Contact Details
    mobile_no = Column(String(20), nullable=False, index=True) # Mob. No.
    email = Column(String(120), nullable=True) # E-mail id
    father_contact_no = Column(String(20), nullable=True) # Father's Contact No.
    alternate_contact_no = Column(String(20), nullable=True) # 2. Contact No.
    permanent_address = Column(Text, nullable=True) # Permanent Address
    district = Column(String(100), nullable=True) # District
    state = Column(String(100), nullable=True) # State
    pin_code = Column(String(20), nullable=True) # Pin

    # Admission & Administrative Status
    status = Column(String(50), default="Active", index=True) # Active, Completed, Dropped, Inquiry
    admission_date = Column(Date, default=date.today, nullable=False)
    declaration_agreed = Column(Boolean, default=True) # Declaration agreed

    # Fees Summary
    total_fee = Column(Float, default=0.0) # Total course fee
    discount_amount = Column(Float, default=0.0) # Scholarship / Discount
    net_fee = Column(Float, default=0.0) # Total - Discount
    fee_remarks = Column(Text, nullable=True) # Fee Remarks

    # Referral Tracking & Commission
    referred_by_student_id = Column(String(36), ForeignKey("students.id", ondelete="SET NULL"), nullable=True, index=True)
    referral_discount = Column(Float, default=0.0) # Discount granted to this student due to referral
    referral_commission = Column(Float, default=0.0) # Commission earned by the referrer for this admission

    # Faculty / Staff Assignment
    assigned_staff_id = Column(String(36), ForeignKey("staff.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relationships
    assigned_staff = relationship("Staff", back_populates="assigned_students")

    # Self-referential relationship for student referrals
    referred_by = relationship(
        "Student",
        remote_side="Student.id",
        foreign_keys=[referred_by_student_id],
        back_populates="referrals",
    )
    referrals = relationship(
        "Student",
        foreign_keys=[referred_by_student_id],
        back_populates="referred_by",
    )

    batch_enrollments = relationship(
        "BatchStudent",
        back_populates="student",
        cascade="all, delete-orphan",
    )

    batches = relationship(
        "Batch",
        secondary="batch_students",
        viewonly=True,
    )

    course_sessions = relationship(
        "StudentCourseSession",
        back_populates="student",
        cascade="all, delete-orphan",
        order_by="StudentCourseSession.session_order",
    )
    
    fee_installments = relationship(
        "StudentFeeInstallment",
        back_populates="student",
        cascade="all, delete-orphan",
        order_by="StudentFeeInstallment.installment_no",
    )

    @property
    def referrals_count(self) -> int:
        """Count of students referred by this student."""
        return len(self.referrals or [])

    @property
    def total_referral_commission_earned(self) -> float:
        """Total commission earned by this student from all referrals."""
        return sum((r.referral_commission or 0.0) for r in (self.referrals or []))

    @property
    def total_referral_discounts_given(self) -> float:
        """Total referral discounts granted across all referred students."""
        return sum((r.referral_discount or 0.0) for r in (self.referrals or []))

    @property
    def total_paid(self) -> float:
        """Calculates total paid amount across all installments."""
        return sum((inst.paid_amount or 0.0) for inst in (self.fee_installments or []))

    @property
    def effective_net_fee(self) -> float:
        """Determines the effective net fee even if total_fee wasn't explicitly entered."""
        if self.net_fee and self.net_fee > 0:
            return self.net_fee
        if self.fee_installments:
            first_due = self.fee_installments[0].due_amount or 0.0
            if first_due > 0:
                return first_due
        paid_sum = self.total_paid
        if paid_sum > 0:
            return paid_sum
        return 0.0

    @property
    def balance_due(self) -> float:
        """Calculates balance remaining on effective net fee."""
        return max(0.0, self.effective_net_fee - self.total_paid)

    @property
    def fee_status(self) -> str:
        """Determines overall fee status."""
        eff_total = self.effective_net_fee
        paid = self.total_paid
        if eff_total <= 0 and paid <= 0:
            return "No Fee"
        if eff_total > 0 and paid >= eff_total:
            return "Paid"
        elif paid > 0:
            return "Partial"
        return "Pending"

    @property
    def latest_paid_installment(self):
        """Returns the most recent installment where a payment was recorded."""
        paid_list = [inst for inst in (self.fee_installments or []) if (inst.paid_amount or 0.0) > 0]
        if not paid_list:
            return None
        return max(
            paid_list,
            key=lambda inst: (inst.payment_date or self.admission_date or date.min, inst.installment_no),
        )

    @property
    def last_payment_date(self):
        """Date of the latest fee payment."""
        latest = self.latest_paid_installment
        if not latest:
            return None
        return latest.payment_date or self.admission_date

    @property
    def days_since_last_payment(self):
        """Number of days elapsed since the latest fee payment."""
        last_dt = self.last_payment_date
        if not last_dt:
            return None
        return max(0, (date.today() - last_dt).days)

    @property
    def last_payment_summary(self) -> str:
        """Formatted summary of last fee payment."""
        last_dt = self.last_payment_date
        if not last_dt:
            return "No Payment"
        days = self.days_since_last_payment
        if days == 0:
            days_str = "Today"
        elif days == 1:
            days_str = "Yesterday"
        else:
            days_str = f"{days}d ago"
        return f"{last_dt.strftime('%d %b %Y')} ({days_str})"



class StudentCourseSession(Base, TimestampMixin):
    """Tracks courses, session breakdown, books issued, and student signature."""
    __tablename__ = "student_course_sessions"

    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    session_order = Column(Integer, default=1) # 1, 2, 3, 4, 5
    course_name = Column(String(200), nullable=False) # e.g. "1st & 2nd-Session", "Full Stack Development"
    book_issued = Column(Boolean, default=False) # Book Issued
    book_details = Column(String(255), nullable=True) # Book name / Date / Remarks
    student_signed = Column(Boolean, default=False) # Student Signature / Acknowledgement

    student = relationship("Student", back_populates="course_sessions")

class StudentFeeInstallment(Base, TimestampMixin):
    """Tracks individual installment payments (1st through 10th)."""
    __tablename__ = "student_fee_installments"

    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    installment_no = Column(Integer, nullable=False) # 1 to 10
    installment_label = Column(String(20), nullable=False) # "1st", "2nd", "3rd", ... "10th"
    due_amount = Column(Float, default=0.0) # Scheduled amount
    paid_amount = Column(Float, default=0.0) # Actually paid amount
    due_date = Column(Date, nullable=True)
    payment_date = Column(Date, nullable=True)
    payment_mode = Column(String(50), nullable=True) # Cash, UPI, Bank Transfer, Cheque
    transaction_ref = Column(String(100), nullable=True) # Receipt No / UTR / Cheque No
    status = Column(String(30), default="Pending") # Pending, Paid, Partial, Overdue
    remarks = Column(String(255), nullable=True)

    student = relationship("Student", back_populates="fee_installments")

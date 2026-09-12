import shutil
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import or_, and_, func
from sqlalchemy.orm import Session, joinedload

from app.core.config import PHOTOS_DIR
from app.core.database import get_db_session
from app.models.student import Student, StudentCourseSession, StudentFeeInstallment
from app.models.custom_fields import CustomFieldDefinition, CustomFieldValue

class StudentController:
    """Handles all business logic, queries, and transactions for Students."""

    @staticmethod
    def get_all_students(
        search_query: Optional[str] = None,
        status_filter: Optional[str] = None,
        course_filter: Optional[str] = None,
        fee_filter: Optional[str] = None,
    ) -> List[Student]:
        """Fetch students with optional filtering and search."""
        with get_db_session() as session:
            query = session.query(Student).options(
                joinedload(Student.course_sessions),
                joinedload(Student.fee_installments),
            )

            if status_filter and status_filter != "All":
                query = query.filter(Student.status == status_filter)

            if course_filter and course_filter != "All":
                query = query.filter(Student.course_name.ilike(f"%{course_filter}%"))

            if search_query:
                term = f"%{search_query.strip()}%"
                query = query.filter(
                    or_(
                        Student.id_no.ilike(term),
                        Student.name.ilike(term),
                        Student.mobile_no.ilike(term),
                        Student.email.ilike(term),
                        Student.father_name.ilike(term),
                        Student.aadhar_no.ilike(term),
                        Student.college_school.ilike(term),
                        Student.district.ilike(term),
                    )
                )

            students = query.order_by(Student.created_at.desc()).all()
            
            # Post-filter on fee status if specified
            if fee_filter and fee_filter != "All":
                if fee_filter == "Paid":
                    students = [s for s in students if s.fee_status == "Paid"]
                elif fee_filter == "Partial":
                    students = [s for s in students if s.fee_status == "Partial"]
                elif fee_filter == "Pending":
                    students = [s for s in students if s.fee_status in ("Pending", "Partial") and s.balance_due > 0]
                elif fee_filter == "No Fee":
                    students = [s for s in students if s.fee_status == "No Fee"]

            # Expunge objects so they can be accessed outside session
            session.expunge_all()
            return students

    @staticmethod
    def get_student_by_id(student_id: str) -> Optional[Student]:
        """Fetch a single student with all relationships."""
        with get_db_session() as session:
            student = (
                session.query(Student)
                .options(
                    joinedload(Student.course_sessions),
                    joinedload(Student.fee_installments),
                )
                .filter(Student.id == student_id)
                .first()
            )
            if student:
                session.expunge_all()
            return student

    @staticmethod
    def generate_next_id_no() -> str:
        """Auto-generate next sequential Student ID No (e.g. CD-2026-0001)."""
        current_year = datetime.now().year
        prefix = f"CD-{current_year}-"
        with get_db_session() as session:
            count = session.query(func.count(Student.id)).filter(Student.id_no.like(f"{prefix}%")).scalar() or 0
            return f"{prefix}{count + 1:04d}"

    @staticmethod
    def save_photo_attachment(source_path: str) -> str:
        """Saves a student photo into local attachments directory and returns relative filename."""
        src = Path(source_path)
        if not src.exists():
            return ""
        ext = src.suffix.lower() or ".jpg"
        filename = f"photo_{uuid.uuid4().hex[:12]}{ext}"
        dest = PHOTOS_DIR / filename
        shutil.copy2(src, dest)
        return filename

    @staticmethod
    def create_student(
        data: Dict[str, Any],
        course_sessions_data: Optional[List[Dict[str, Any]]] = None,
        fee_installments_data: Optional[List[Dict[str, Any]]] = None,
        custom_values: Optional[Dict[str, str]] = None,
    ) -> Student:
        """Create a new student with optional course sessions, installments, and custom field values."""
        course_sessions_data = course_sessions_data or []
        fee_installments_data = fee_installments_data or []
        custom_values = custom_values or {}
        with get_db_session() as session:
            # Create core Student
            student = Student(
                id_no=data.get("id_no") or StudentController.generate_next_id_no(),
                is_online=data.get("is_online", False),
                online_reg_no=data.get("online_reg_no"),
                photo_path=data.get("photo_path"),
                name=data.get("name", "").strip(),
                father_name=data.get("father_name"),
                mother_name=data.get("mother_name"),
                dob=data.get("dob"),
                father_occupation=data.get("father_occupation"),
                college_school=data.get("college_school"),
                course_name=data.get("course_name"),
                year_sem=data.get("year_sem"),
                aadhar_no=data.get("aadhar_no"),
                mobile_no=data.get("mobile_no", "").strip(),
                email=data.get("email"),
                father_contact_no=data.get("father_contact_no"),
                alternate_contact_no=data.get("alternate_contact_no"),
                permanent_address=data.get("permanent_address"),
                district=data.get("district"),
                state=data.get("state"),
                pin_code=data.get("pin_code"),
                status=data.get("status", "Active"),
                admission_date=data.get("admission_date") or date.today(),
                declaration_agreed=data.get("declaration_agreed", True),
                total_fee=float(data.get("total_fee") or 0.0),
                discount_amount=float(data.get("discount_amount") or 0.0),
                net_fee=float(data.get("net_fee") or 0.0),
                fee_remarks=data.get("fee_remarks"),
            )
            session.add(student)
            session.flush() # Populate student.id

            # Add Course Sessions
            for idx, cs in enumerate(course_sessions_data, start=1):
                c_name = cs.get("course_name", "").strip()
                if c_name:
                    session_obj = StudentCourseSession(
                        student_id=student.id,
                        session_order=idx,
                        course_name=c_name,
                        book_issued=bool(cs.get("book_issued", False)),
                        book_details=cs.get("book_details"),
                        student_signed=bool(cs.get("student_signed", False)),
                    )
                    session.add(session_obj)

            # Add Fee Installments (up to 10)
            running_due = float(student.net_fee or 0.0)
            for idx, inst in enumerate(fee_installments_data):
                inst_no = int(inst.get("installment_no", idx + 1))
                paid_amt = float(inst.get("paid_amount") or 0.0)

                # Compute running due
                if paid_amt > 0 or idx == 0:
                    due_amt = running_due
                elif running_due > 0 and idx > 0 and (float(fee_installments_data[idx - 1].get("paid_amount") or 0.0) > 0):
                    due_amt = running_due
                elif inst.get("due_amount") is not None and float(inst.get("due_amount") or 0.0) > 0:
                    due_amt = float(inst.get("due_amount"))
                else:
                    due_amt = 0.0

                # Determine status
                if paid_amt > 0:
                    status = "Paid"
                elif due_amt > 0:
                    status = "Pending"
                else:
                    status = "Pending"

                installment_obj = StudentFeeInstallment(
                    student_id=student.id,
                    installment_no=inst_no,
                    installment_label=inst.get("installment_label", f"{inst_no}th"),
                    due_amount=due_amt,
                    paid_amount=paid_amt,
                    due_date=inst.get("due_date"),
                    payment_date=inst.get("payment_date"),
                    payment_mode=inst.get("payment_mode"),
                    transaction_ref=inst.get("transaction_ref"),
                    status=status,
                    remarks=inst.get("remarks"),
                )
                session.add(installment_obj)
                running_due = max(0.0, running_due - paid_amt)

            # Save Custom Field Values
            for field_id, val_str in custom_values.items():
                if val_str is not None and str(val_str).strip() != "":
                    cf_val = CustomFieldValue(
                        entity_id=student.id,
                        field_id=field_id,
                        value_text=str(val_str),
                    )
                    session.add(cf_val)

            session.commit()
            student_id = student.id

        return StudentController.get_student_by_id(student_id)

    @staticmethod
    def update_student(
        student_id: str,
        data: Dict[str, Any],
        course_sessions_data: Optional[List[Dict[str, Any]]] = None,
        fee_installments_data: Optional[List[Dict[str, Any]]] = None,
        custom_values: Optional[Dict[str, str]] = None,
    ) -> Optional[Student]:
        """Update an existing student record, course sessions, installments, and custom fields."""
        course_sessions_data = course_sessions_data or []
        fee_installments_data = fee_installments_data or []
        custom_values = custom_values or {}
        with get_db_session() as session:
            student = session.query(Student).filter(Student.id == student_id).first()
            if not student:
                return None

            # Update core attributes
            for key in [
                "id_no", "is_online", "online_reg_no", "photo_path", "name", "father_name",
                "mother_name", "dob", "father_occupation", "college_school", "course_name",
                "year_sem", "aadhar_no", "mobile_no", "email", "father_contact_no",
                "alternate_contact_no", "permanent_address", "district", "state", "pin_code",
                "status", "admission_date", "declaration_agreed", "total_fee", "discount_amount",
                "net_fee", "fee_remarks"
            ]:
                if key in data:
                    setattr(student, key, data[key])

            # Replace Course Sessions
            session.query(StudentCourseSession).filter(StudentCourseSession.student_id == student_id).delete()
            for idx, cs in enumerate(course_sessions_data, start=1):
                c_name = cs.get("course_name", "").strip()
                if c_name:
                    session_obj = StudentCourseSession(
                        student_id=student.id,
                        session_order=idx,
                        course_name=c_name,
                        book_issued=bool(cs.get("book_issued", False)),
                        book_details=cs.get("book_details"),
                        student_signed=bool(cs.get("student_signed", False)),
                    )
                    session.add(session_obj)

            # Replace Fee Installments
            session.query(StudentFeeInstallment).filter(StudentFeeInstallment.student_id == student_id).delete()
            running_due = float(student.net_fee or 0.0)
            for idx, inst in enumerate(fee_installments_data):
                inst_no = int(inst.get("installment_no", idx + 1))
                paid_amt = float(inst.get("paid_amount") or 0.0)

                # Compute running due
                if paid_amt > 0 or idx == 0:
                    due_amt = running_due
                elif running_due > 0 and idx > 0 and (float(fee_installments_data[idx - 1].get("paid_amount") or 0.0) > 0):
                    due_amt = running_due
                elif inst.get("due_amount") is not None and float(inst.get("due_amount") or 0.0) > 0:
                    due_amt = float(inst.get("due_amount"))
                else:
                    due_amt = 0.0

                # Determine status
                if paid_amt > 0:
                    status = "Paid"
                elif due_amt > 0:
                    status = "Pending"
                else:
                    status = "Pending"

                installment_obj = StudentFeeInstallment(
                    student_id=student.id,
                    installment_no=inst_no,
                    installment_label=inst.get("installment_label", f"{inst_no}th"),
                    due_amount=due_amt,
                    paid_amount=paid_amt,
                    due_date=inst.get("due_date"),
                    payment_date=inst.get("payment_date"),
                    payment_mode=inst.get("payment_mode"),
                    transaction_ref=inst.get("transaction_ref"),
                    status=status,
                    remarks=inst.get("remarks"),
                )
                session.add(installment_obj)
                running_due = max(0.0, running_due - paid_amt)

            # Replace Custom Field Values
            session.query(CustomFieldValue).filter(CustomFieldValue.entity_id == student_id).delete()
            for field_id, val_str in custom_values.items():
                if val_str is not None and str(val_str).strip() != "":
                    cf_val = CustomFieldValue(
                        entity_id=student.id,
                        field_id=field_id,
                        value_text=str(val_str),
                    )
                    session.add(cf_val)

            session.commit()

        return StudentController.get_student_by_id(student_id)

    @staticmethod
    def delete_student(student_id: str) -> bool:
        """Deletes a student and associated data."""
        with get_db_session() as session:
            student = session.query(Student).filter(Student.id == student_id).first()
            if not student:
                return False
            # Clean up photo file if exists
            if student.photo_path:
                photo_file = PHOTOS_DIR / student.photo_path
                if photo_file.exists():
                    try:
                        photo_file.unlink()
                    except Exception:
                        pass
            session.delete(student)
            session.commit()
            return True

    @staticmethod
    def get_student_custom_values(student_id: str) -> Dict[str, str]:
        """Fetch custom field values dictionary for a given student ID."""
        with get_db_session() as session:
            values = session.query(CustomFieldValue).filter(CustomFieldValue.entity_id == student_id).all()
            return {v.field_id: v.value_text for v in values}

    @staticmethod
    def get_custom_field_definitions(entity_type: str = "student") -> List[CustomFieldDefinition]:
        """Fetch all defined custom fields for students."""
        with get_db_session() as session:
            defs = (
                session.query(CustomFieldDefinition)
                .filter(CustomFieldDefinition.entity_type == entity_type)
                .order_by(CustomFieldDefinition.sort_order.asc(), CustomFieldDefinition.created_at.asc())
                .all()
            )
            session.expunge_all()
            return defs

    @staticmethod
    def save_custom_field_definition(
        field_label: str,
        field_type: str,
        options: Optional[List[str]] = None,
        is_required: bool = False,
        entity_type: str = "student",
    ) -> CustomFieldDefinition:
        """Creates a new runtime custom field definition."""
        field_name = field_label.lower().replace(" ", "_").replace("-", "_")
        with get_db_session() as session:
            cf = CustomFieldDefinition(
                entity_type=entity_type,
                field_name=field_name,
                field_label=field_label,
                field_type=field_type,
                is_required=is_required,
            )
            if options:
                cf.set_options(options)
            session.add(cf)
            session.commit()
            session.refresh(cf)
            session.expunge_all()
            return cf

    @staticmethod
    def delete_custom_field_definition(field_id: str) -> bool:
        """Deletes a custom field definition and all its associated values."""
        with get_db_session() as session:
            cf = session.query(CustomFieldDefinition).filter(CustomFieldDefinition.id == field_id).first()
            if not cf:
                return False
            session.delete(cf)
            session.commit()
            return True

    @staticmethod
    def get_dashboard_metrics() -> Dict[str, Any]:
        """Calculates dashboard summary metrics."""
        with get_db_session() as session:
            total_students = session.query(func.count(Student.id)).scalar() or 0
            active_students = session.query(func.count(Student.id)).filter(Student.status == "Active").scalar() or 0
            
            # Total net fee
            total_fee_sum = session.query(func.sum(Student.net_fee)).scalar() or 0.0
            
            # Total paid across all installments
            total_paid_sum = session.query(func.sum(StudentFeeInstallment.paid_amount)).scalar() or 0.0
            
            # Books issued count
            books_issued_count = (
                session.query(func.count(StudentCourseSession.id))
                .filter(StudentCourseSession.book_issued == True)  # noqa: E712
                .scalar() or 0
            )

            balance_due = max(0.0, total_fee_sum - total_paid_sum)

            return {
                "total_students": total_students,
                "active_students": active_students,
                "total_fee": total_fee_sum,
                "total_paid": total_paid_sum,
                "balance_due": balance_due,
                "books_issued": books_issued_count,
            }

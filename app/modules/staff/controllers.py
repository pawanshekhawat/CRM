from datetime import date, datetime
import logging
from typing import Any, Dict, List, Optional
from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from app.core.database import get_db_session
from app.models.staff import Batch, BatchStudent, Staff
from app.models.student import Student

logger = logging.getLogger("CRM.StaffController")

DEFAULT_STAFF_MEMBERS = [
    {
        "staff_id": "STF-001",
        "name": "Ramgopal Kumawat Ji",
        "designation": None,
        "department": None,
        "mobile_no": None,
        "status": "Active",
    },
    {
        "staff_id": "STF-002",
        "name": "Aadil ji",
        "designation": None,
        "department": None,
        "mobile_no": None,
        "status": "Active",
    },
    {
        "staff_id": "STF-003",
        "name": "Ayan JI",
        "designation": None,
        "department": None,
        "mobile_no": None,
        "status": "Active",
    },
    {
        "staff_id": "STF-004",
        "name": "Sahil Khan",
        "designation": None,
        "department": None,
        "mobile_no": None,
        "status": "Active",
    },
    {
        "staff_id": "STF-005",
        "name": "Zaid Chauhan",
        "designation": None,
        "department": None,
        "mobile_no": None,
        "status": "Active",
    },
    {
        "staff_id": "STF-006",
        "name": "Hemant Verma",
        "designation": None,
        "department": None,
        "mobile_no": None,
        "status": "Active",
    },
    {
        "staff_id": "STF-007",
        "name": "Monika",
        "designation": "Receptionist",
        "department": None,
        "mobile_no": None,
        "status": "Active",
    },
]

class StaffController:
    """Controller handling business logic for Staff, Batches, and Student Rosters."""

    # ==========================================
    # 1. Staff Operations
    # ==========================================

    @staticmethod
    def seed_default_staff_if_empty() -> int:
        """Seeds real staff members if the staff directory is empty."""
        with get_db_session() as session:
            count = session.query(func.count(Staff.id)).scalar() or 0
            if count > 0:
                return 0

            seeded = 0
            for item in DEFAULT_STAFF_MEMBERS:
                staff = Staff(
                    staff_id=item["staff_id"],
                    name=item["name"],
                    designation=item.get("designation"),
                    department=item.get("department"),
                    mobile_no=item.get("mobile_no"),
                    status=item.get("status", "Active"),
                    joining_date=date.today(),
                )
                session.add(staff)
                seeded += 1
            session.commit()
            if seeded > 0:
                logger.info(f"Seeded {seeded} real staff members into staff directory.")
            return seeded

    @staticmethod
    def generate_next_staff_id() -> str:
        """Generates the next sequential Staff ID (e.g. STF-001)."""
        with get_db_session() as session:
            count = session.query(func.count(Staff.id)).scalar() or 0
            return f"STF-{(count + 1):03d}"

    @staticmethod
    def get_all_staff(
        search: Optional[str] = None,
        department: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Staff]:
        """Fetches staff members with filtering."""
        with get_db_session() as session:
            query = session.query(Staff).options(
                joinedload(Staff.batches).joinedload(Batch.enrollments),
                joinedload(Staff.assigned_students),
            )

            if search:
                term = f"%{search.strip()}%"
                query = query.filter(
                    or_(
                        Staff.name.ilike(term),
                        Staff.staff_id.ilike(term),
                        Staff.mobile_no.ilike(term),
                        Staff.designation.ilike(term),
                        Staff.email.ilike(term),
                    )
                )

            if department and department != "All":
                query = query.filter(Staff.department == department)

            if status and status != "All":
                query = query.filter(Staff.status == status)

            staff_list = query.order_by(Staff.staff_id.asc()).all()
            session.expunge_all()
            return staff_list

    @staticmethod
    def get_staff_by_id(staff_id: str) -> Optional[Staff]:
        """Fetches a staff member with full batches and assigned students loaded."""
        with get_db_session() as session:
            staff = session.query(Staff).options(
                joinedload(Staff.batches).joinedload(Batch.enrollments).joinedload(BatchStudent.student),
                joinedload(Staff.assigned_students),
            ).filter(Staff.id == staff_id).first()
            if staff:
                session.expunge_all()
            return staff

    @staticmethod
    def create_staff(data: Dict[str, Any]) -> Staff:
        """Creates a new staff member."""
        with get_db_session() as session:
            staff_id_code = data.get("staff_id") or StaffController.generate_next_staff_id()

            staff = Staff(
                staff_id=staff_id_code,
                name=data["name"].strip(),
                designation=data.get("designation", "").strip() if data.get("designation") else None,
                department=data.get("department", "").strip() if data.get("department") else None,
                mobile_no=data.get("mobile_no", "").strip() if data.get("mobile_no") else None,
                email=data.get("email", "").strip() if data.get("email") else None,
                qualification=data.get("qualification", "").strip() if data.get("qualification") else None,
                joining_date=data.get("joining_date") or date.today(),
                salary=float(data.get("salary") or 0.0),
                status=data.get("status", "Active"),
                photo_path=data.get("photo_path"),
                notes=data.get("notes"),
            )
            session.add(staff)
            session.flush()
            target_id = staff.id
            session.commit()
            logger.info(f"Created staff member: {staff.name} ({staff.staff_id})")

        return StaffController.get_staff_by_id(target_id)

    @staticmethod
    def update_staff(staff_id: str, data: Dict[str, Any]) -> Optional[Staff]:
        """Updates an existing staff record."""
        with get_db_session() as session:
            staff = session.query(Staff).filter(Staff.id == staff_id).first()
            if not staff:
                return None

            for field in [
                "staff_id", "name", "designation", "department", "mobile_no", "email",
                "qualification", "joining_date", "salary", "status", "photo_path", "notes"
            ]:
                if field in data:
                    setattr(staff, field, data[field])

            session.commit()
            logger.info(f"Updated staff member: {staff.name} ({staff.staff_id})")

        return StaffController.get_staff_by_id(staff_id)

    @staticmethod
    def delete_staff(staff_id: str) -> bool:
        """Deletes a staff member (unlinks batches & assigned students)."""
        with get_db_session() as session:
            staff = session.query(Staff).filter(Staff.id == staff_id).first()
            if not staff:
                return False

            session.delete(staff)
            session.commit()
            logger.info(f"Deleted staff member ID: {staff_id}")
            return True

    # ==========================================
    # 2. Batch Operations
    # ==========================================

    @staticmethod
    def generate_next_batch_code(prefix: str = "BAT") -> str:
        """Generates a unique batch code."""
        with get_db_session() as session:
            count = session.query(func.count(Batch.id)).scalar() or 0
            return f"{prefix}-{(count + 1):03d}"

    @staticmethod
    def get_all_batches(
        staff_id: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Batch]:
        """Fetches all batches with instructor and enrollments loaded."""
        with get_db_session() as session:
            query = session.query(Batch).options(
                joinedload(Batch.instructor),
                joinedload(Batch.enrollments).joinedload(BatchStudent.student),
            )

            if staff_id and staff_id != "All":
                query = query.filter(Batch.staff_id == staff_id)

            if status and status != "All":
                query = query.filter(Batch.status == status)

            if search:
                term = f"%{search.strip()}%"
                query = query.filter(
                    or_(
                        Batch.batch_code.ilike(term),
                        Batch.batch_name.ilike(term),
                        Batch.course_name.ilike(term),
                        Batch.room_lab.ilike(term),
                    )
                )

            batches = query.order_by(Batch.created_at.desc()).all()
            session.expunge_all()
            return batches

    @staticmethod
    def get_batch_by_id(batch_id: str) -> Optional[Batch]:
        """Fetches a batch by ID with full details."""
        with get_db_session() as session:
            batch = session.query(Batch).options(
                joinedload(Batch.instructor),
                joinedload(Batch.enrollments).joinedload(BatchStudent.student),
            ).filter(Batch.id == batch_id).first()
            if batch:
                session.expunge_all()
            return batch

    @staticmethod
    def create_batch(data: Dict[str, Any]) -> Batch:
        """Creates a new batch."""
        with get_db_session() as session:
            code = data.get("batch_code") or StaffController.generate_next_batch_code()
            batch = Batch(
                batch_code=code.strip(),
                batch_name=data["batch_name"].strip(),
                course_name=data.get("course_name", "").strip() if data.get("course_name") else None,
                staff_id=data.get("staff_id"),
                start_time=data.get("start_time", "09:00 AM"),
                end_time=data.get("end_time", "11:00 AM"),
                days_schedule=data.get("days_schedule", "Mon-Fri"),
                room_lab=data.get("room_lab", "Lab 1"),
                start_date=data.get("start_date") or date.today(),
                end_date=data.get("end_date"),
                max_capacity=int(data.get("max_capacity") or 20),
                status=data.get("status", "Active"),
                remarks=data.get("remarks"),
            )
            session.add(batch)
            session.flush()
            target_id = batch.id
            session.commit()
            logger.info(f"Created batch: {batch.batch_name} ({batch.batch_code})")

        return StaffController.get_batch_by_id(target_id)

    @staticmethod
    def update_batch(batch_id: str, data: Dict[str, Any]) -> Optional[Batch]:
        """Updates a batch."""
        with get_db_session() as session:
            batch = session.query(Batch).filter(Batch.id == batch_id).first()
            if not batch:
                return None

            for field in [
                "batch_code", "batch_name", "course_name", "staff_id", "start_time",
                "end_time", "days_schedule", "room_lab", "start_date", "end_date",
                "max_capacity", "status", "remarks"
            ]:
                if field in data:
                    setattr(batch, field, data[field])

            session.commit()
            logger.info(f"Updated batch: {batch.batch_name} ({batch.batch_code})")

        return StaffController.get_batch_by_id(batch_id)

    @staticmethod
    def delete_batch(batch_id: str) -> bool:
        """Deletes a batch and its enrollment links."""
        with get_db_session() as session:
            batch = session.query(Batch).filter(Batch.id == batch_id).first()
            if not batch:
                return False

            session.delete(batch)
            session.commit()
            logger.info(f"Deleted batch ID: {batch_id}")
            return True

    # ==========================================
    # 3. Batch Roster & Student Allocations
    # ==========================================

    @staticmethod
    def enroll_student_in_batch(batch_id: str, student_id: str, remarks: Optional[str] = None) -> Optional[BatchStudent]:
        """Enrolls a student in a batch."""
        with get_db_session() as session:
            # Check if already enrolled
            existing = session.query(BatchStudent).filter(
                BatchStudent.batch_id == batch_id,
                BatchStudent.student_id == student_id,
            ).first()

            if existing:
                existing.status = "Active"
                if remarks:
                    existing.remarks = remarks
                session.commit()
                session.expunge_all()
                return existing

            enrollment = BatchStudent(
                batch_id=batch_id,
                student_id=student_id,
                enrolled_date=date.today(),
                status="Active",
                remarks=remarks,
            )
            session.add(enrollment)
            session.commit()
            session.expunge_all()
            logger.info(f"Enrolled student {student_id} into batch {batch_id}")
            return enrollment

    @staticmethod
    def remove_student_from_batch(batch_id: str, student_id: str) -> bool:
        """Removes an enrollment link from a batch."""
        with get_db_session() as session:
            enrollment = session.query(BatchStudent).filter(
                BatchStudent.batch_id == batch_id,
                BatchStudent.student_id == student_id,
            ).first()

            if not enrollment:
                return False

            session.delete(enrollment)
            session.commit()
            logger.info(f"Removed student {student_id} from batch {batch_id}")
            return True

    @staticmethod
    def get_unassigned_students_for_batch(batch_id: str, search: Optional[str] = None) -> List[Student]:
        """Gets active students who are NOT yet enrolled in the specified batch."""
        with get_db_session() as session:
            # Get already enrolled student IDs
            enrolled_subquery = session.query(BatchStudent.student_id).filter(
                BatchStudent.batch_id == batch_id,
                BatchStudent.status == "Active",
            ).subquery()

            query = session.query(Student).filter(
                ~Student.id.in_(enrolled_subquery),
                Student.status == "Active",
            )

            if search:
                term = f"%{search.strip()}%"
                query = query.filter(
                    or_(
                        Student.name.ilike(term),
                        Student.id_no.ilike(term),
                        Student.mobile_no.ilike(term),
                        Student.course_name.ilike(term),
                    )
                )

            students = query.order_by(Student.name.asc()).limit(50).all()
            session.expunge_all()
            return students

    @staticmethod
    def assign_student_to_staff(student_id: str, staff_id: Optional[str]) -> bool:
        """Directly assigns a student to a primary faculty mentor."""
        with get_db_session() as session:
            student = session.query(Student).filter(Student.id == student_id).first()
            if not student:
                return False
            student.assigned_staff_id = staff_id
            session.commit()
            return True

    @staticmethod
    def get_staff_dashboard_metrics() -> Dict[str, Any]:
        """Calculates dashboard metrics for the Staff & Batches module."""
        with get_db_session() as session:
            total_staff = session.query(func.count(Staff.id)).scalar() or 0
            active_staff = session.query(func.count(Staff.id)).filter(Staff.status == "Active").scalar() or 0
            total_batches = session.query(func.count(Batch.id)).scalar() or 0
            active_batches = session.query(func.count(Batch.id)).filter(Batch.status == "Active").scalar() or 0
            active_enrollments = session.query(func.count(BatchStudent.id)).filter(BatchStudent.status == "Active").scalar() or 0

            return {
                "total_staff": total_staff,
                "active_staff": active_staff,
                "total_batches": total_batches,
                "active_batches": active_batches,
                "active_enrollments": active_enrollments,
            }

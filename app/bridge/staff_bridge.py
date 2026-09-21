import json
import logging
from datetime import datetime, date
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Signal, Slot

from app.modules.staff.controllers import StaffController

logger = logging.getLogger("CRM.StaffBridge")


def serialize_staff(staff: Any) -> Dict[str, Any]:
    """Serializes a Staff model for QML."""
    if not staff:
        return {}

    batch_count = len(staff.batches) if hasattr(staff, "batches") and staff.batches else 0
    assigned_count = len(staff.assigned_students) if hasattr(staff, "assigned_students") and staff.assigned_students else 0

    return {
        "id": str(staff.id),
        "staff_id": staff.staff_id or "",
        "name": staff.name or "",
        "designation": staff.designation or "Faculty",
        "department": staff.department or "Academics",
        "mobile_no": staff.mobile_no or "",
        "email": staff.email or "",
        "qualification": staff.qualification or "",
        "joining_date": staff.joining_date.strftime("%Y-%m-%d") if staff.joining_date else "",
        "salary": float(staff.salary or 0.0),
        "status": staff.status or "Active",
        "notes": staff.notes or "",
        "batch_count": batch_count,
        "assigned_student_count": assigned_count,
    }


def serialize_batch(batch: Any) -> Dict[str, Any]:
    """Serializes a Batch model including instructor and roster counts for QML."""
    if not batch:
        return {}

    instructor_name = batch.instructor.name if batch.instructor else "Unassigned"
    enrolled_count = len(batch.enrollments) if hasattr(batch, "enrollments") and batch.enrollments else 0

    roster = []
    if hasattr(batch, "enrollments") and batch.enrollments:
        for enr in batch.enrollments:
            if enr.student:
                s = enr.student
                roster.append({
                    "enrollment_id": str(enr.id),
                    "student_id": s.id,
                    "id_no": s.id_no or "",
                    "name": s.name or "",
                    "mobile_no": s.mobile_no or "",
                    "enrolled_date": enr.enrolled_date.strftime("%Y-%m-%d") if enr.enrolled_date else "",
                    "status": enr.status or "Active",
                    "fee_status": s.fee_status or "Pending",
                    "balance_due": float(s.balance_due or 0.0),
                })

    return {
        "id": str(batch.id),
        "batch_code": batch.batch_code or "",
        "batch_name": batch.batch_name or "",
        "course_name": batch.course_name or "",
        "staff_id": str(batch.staff_id) if batch.staff_id else "",
        "instructor_name": instructor_name,
        "start_time": batch.start_time or "09:00 AM",
        "end_time": batch.end_time or "11:00 AM",
        "days_schedule": batch.days_schedule or "Mon-Fri",
        "room_lab": batch.room_lab or "Lab 1",
        "start_date": batch.start_date.strftime("%Y-%m-%d") if batch.start_date else "",
        "end_date": batch.end_date.strftime("%Y-%m-%d") if batch.end_date else "",
        "max_capacity": int(batch.max_capacity or 20),
        "enrolled_count": enrolled_count,
        "status": batch.status or "Active",
        "remarks": batch.remarks or "",
        "roster": roster,
    }


class StaffBridge(QObject):
    """Bridge for Staff Members, Batches, and Student Rosters."""

    staffChanged = Signal()
    batchesChanged = Signal()
    staffSaved = Signal(bool, str, str)
    batchSaved = Signal(bool, str, str)
    rosterUpdated = Signal(bool, str)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

    # ------------------ Staff ------------------

    @Slot(result="QVariantList")
    @Slot(str, result="QVariantList")
    @Slot(str, str, result="QVariantList")
    @Slot(str, str, str, result="QVariantList")
    def getStaffList(
        self,
        search: str = "",
        department: str = "All",
        status: str = "All",
    ) -> List[Dict[str, Any]]:
        """Fetches staff members with filtering."""
        try:
            staff_list = StaffController.get_all_staff(
                search=search if search.strip() else None,
                department=department if department != "All" else None,
                status=status if status != "All" else None,
            )
            return [serialize_staff(s) for s in staff_list]
        except Exception as e:
            logger.error(f"Error fetching staff: {e}")
            return []

    @Slot(str, result="QVariantMap")
    def getStaffById(self, staff_id: str) -> Dict[str, Any]:
        """Fetches a staff member by ID."""
        try:
            staff = StaffController.get_staff_by_id(staff_id)
            return serialize_staff(staff)
        except Exception as e:
            logger.error(f"Error fetching staff {staff_id}: {e}")
            return {}

    @Slot(str, result="QVariantMap")
    def saveStaff(self, data_json: str) -> Dict[str, Any]:
        """Creates or updates a staff member."""
        try:
            data = json.loads(data_json)
            staff_id = data.get("id")

            if "joining_date" in data and data["joining_date"]:
                try:
                    data["joining_date"] = datetime.strptime(data["joining_date"][:10], "%Y-%m-%d").date()
                except Exception:
                    pass

            if staff_id:
                staff = StaffController.update_staff(staff_id, data)
                if not staff:
                    return {"success": False, "message": "Staff not found", "id": ""}
                msg = f"Staff member {staff.name} updated."
                ret_id = str(staff.id)
            else:
                staff = StaffController.create_staff(data)
                msg = f"Staff member {staff.name} registered with ID {staff.staff_id}."
                ret_id = str(staff.id)

            self.staffChanged.emit()
            self.staffSaved.emit(True, msg, ret_id)
            return {"success": True, "message": msg, "id": ret_id}

        except Exception as e:
            logger.error(f"Error saving staff: {e}")
            self.staffSaved.emit(False, str(e), "")
            return {"success": False, "message": str(e), "id": ""}

    @Slot(str, result=bool)
    def deleteStaff(self, staff_id: str) -> bool:
        """Deletes a staff member."""
        try:
            success = StaffController.delete_staff(staff_id)
            if success:
                self.staffChanged.emit()
            return success
        except Exception as e:
            logger.error(f"Error deleting staff {staff_id}: {e}")
            return False

    # ------------------ Batches ------------------

    @Slot(result="QVariantList")
    @Slot(str, result="QVariantList")
    @Slot(str, str, result="QVariantList")
    @Slot(str, str, str, result="QVariantList")
    def getBatches(
        self,
        staff_id: str = "All",
        status: str = "All",
        search: str = "",
    ) -> List[Dict[str, Any]]:
        """Fetches batches with filtering."""
        try:
            batches = StaffController.get_all_batches(
                staff_id=staff_id if staff_id != "All" else None,
                status=status if status != "All" else None,
                search=search if search.strip() else None,
            )
            return [serialize_batch(b) for b in batches]
        except Exception as e:
            logger.error(f"Error fetching batches: {e}")
            return []

    @Slot(str, result="QVariantMap")
    def getBatchById(self, batch_id: str) -> Dict[str, Any]:
        """Fetches batch details including roster."""
        try:
            batch = StaffController.get_batch_by_id(batch_id)
            return serialize_batch(batch)
        except Exception as e:
            logger.error(f"Error fetching batch {batch_id}: {e}")
            return {}

    @Slot(str, result="QVariantMap")
    def saveBatch(self, data_json: str) -> Dict[str, Any]:
        """Creates or updates a batch schedule."""
        try:
            data = json.loads(data_json)
            batch_id = data.get("id")

            for date_field in ["start_date", "end_date"]:
                if date_field in data and data[date_field]:
                    try:
                        data[date_field] = datetime.strptime(data[date_field][:10], "%Y-%m-%d").date()
                    except Exception:
                        pass

            if batch_id:
                batch = StaffController.update_batch(batch_id, data)
                if not batch:
                    return {"success": False, "message": "Batch not found", "id": ""}
                msg = f"Batch {batch.batch_name} updated."
                ret_id = str(batch.id)
            else:
                batch = StaffController.create_batch(data)
                msg = f"Batch {batch.batch_name} created with code {batch.batch_code}."
                ret_id = str(batch.id)

            self.batchesChanged.emit()
            self.batchSaved.emit(True, msg, ret_id)
            return {"success": True, "message": msg, "id": ret_id}

        except Exception as e:
            logger.error(f"Error saving batch: {e}")
            self.batchSaved.emit(False, str(e), "")
            return {"success": False, "message": str(e), "id": ""}

    @Slot(str, result=bool)
    def deleteBatch(self, batch_id: str) -> bool:
        """Deletes a batch."""
        try:
            success = StaffController.delete_batch(batch_id)
            if success:
                self.batchesChanged.emit()
            return success
        except Exception as e:
            logger.error(f"Error deleting batch {batch_id}: {e}")
            return False

    @Slot(str, str, str, result=bool)
    def enrollStudent(self, batch_id: str, student_id: str, remarks: str = "") -> bool:
        """Enrolls a student in a batch."""
        try:
            enrollment = StaffController.enroll_student_in_batch(batch_id, student_id, remarks)
            if enrollment:
                self.batchesChanged.emit()
                self.rosterUpdated.emit(True, "Student enrolled successfully.")
                return True
            return False
        except Exception as e:
            logger.error(f"Error enrolling student: {e}")
            self.rosterUpdated.emit(False, str(e))
            return False

    @Slot(str, str, result=bool)
    def removeStudentFromBatch(self, batch_id: str, student_id: str) -> bool:
        """Removes a student from batch roster."""
        try:
            success = StaffController.remove_student_from_batch(batch_id, student_id)
            if success:
                self.batchesChanged.emit()
                self.rosterUpdated.emit(True, "Student removed from batch roster.")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing student from batch: {e}")
            self.rosterUpdated.emit(False, str(e))
            return False

    @Slot(str, str, result="QVariantList")
    def getUnassignedStudents(self, batch_id: str, search: str = "") -> List[Dict[str, Any]]:
        """Gets students not enrolled in this batch for the Add to Roster modal."""
        try:
            students = StaffController.get_unassigned_students_for_batch(batch_id, search if search.strip() else None)
            return [
                {
                    "id": s.id,
                    "id_no": s.id_no or "",
                    "name": s.name or "",
                    "course_name": s.course_name or "",
                    "mobile_no": s.mobile_no or "",
                }
                for s in students
            ]
        except Exception as e:
            logger.error(f"Error fetching unassigned students: {e}")
            return []

    @Slot(result="QVariantList")
    def getStaffNames(self) -> List[Dict[str, str]]:
        """Returns list of staff with id and name for dropdowns."""
        try:
            staff_list = StaffController.get_all_staff(status="Active")
            return [{"id": str(s.id), "name": s.name} for s in staff_list]
        except Exception as e:
            logger.error(f"Error fetching staff dropdown: {e}")
            return []

    @Slot(result="QVariantMap")
    def getMetrics(self) -> Dict[str, Any]:
        """Fetches module dashboard metrics."""
        try:
            return StaffController.get_staff_dashboard_metrics()
        except Exception as e:
            logger.error(f"Error fetching staff metrics: {e}")
            return {"total_staff": 0, "active_staff": 0, "total_batches": 0, "active_batches": 0, "active_enrollments": 0}

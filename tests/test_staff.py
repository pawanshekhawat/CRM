import pytest
from datetime import date

from app.core.database import init_db
from app.modules.staff.controllers import StaffController
from app.modules.students.controllers import StudentController

import uuid

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_db()

def test_staff_crud_lifecycle():
    uid = uuid.uuid4().hex[:6]
    staff_id_val = f"STF-TEST-{uid}"

    # 1. Create Staff
    staff_data = {
        "staff_id": staff_id_val,
        "name": "Er. Rajesh Sharma",
        "designation": "Senior Architecture Faculty",
        "department": "Civil / Architecture",
        "mobile_no": "9876500010",
        "email": "rajesh.test@caddesk.com",
        "qualification": "B.Tech Civil, Autodesk Revit Certified",
        "salary": 35000.0,
        "status": "Active",
        "joining_date": date(2023, 5, 1),
    }

    staff = StaffController.create_staff(staff_data)
    assert staff is not None
    assert staff.id is not None
    assert staff.name == "Er. Rajesh Sharma"
    assert staff.staff_id == staff_id_val
    assert staff.designation == "Senior Architecture Faculty"

    # 2. Update Staff
    updated = StaffController.update_staff(staff.id, {"designation": "Head of Architecture Faculty", "salary": 40000.0})
    assert updated.designation == "Head of Architecture Faculty"
    assert updated.salary == 40000.0

    # 3. Retrieve
    retrieved = StaffController.get_staff_by_id(staff.id)
    assert retrieved is not None
    assert retrieved.name == "Er. Rajesh Sharma"

    # 4. Clean up
    deleted = StaffController.delete_staff(staff.id)
    assert deleted is True


def test_batch_and_student_roster_allocation():
    uid = uuid.uuid4().hex[:6]
    staff_id_val = f"STF-BAT-{uid}"
    batch_code_val = f"BAT-{uid}"
    student_id_val = f"CD-BAT-{uid}"

    # 1. Create Staff Instructor
    staff = StaffController.create_staff({
        "staff_id": staff_id_val,
        "name": "Prof. Amit Verma",
        "designation": "AutoCAD Instructor",
        "mobile_no": "9876500020",
        "status": "Active",
    })

    # 2. Create Batch
    batch_data = {
        "batch_code": batch_code_val,
        "batch_name": "Morning Architecture Master 9AM",
        "course_name": "Master in Architecture",
        "staff_id": staff.id,
        "start_time": "09:00 AM",
        "end_time": "11:00 AM",
        "days_schedule": "Mon-Fri",
        "room_lab": "Lab 1",
        "max_capacity": 15,
        "status": "Active",
    }
    batch = StaffController.create_batch(batch_data)
    assert batch is not None
    assert batch.batch_code == batch_code_val
    assert batch.instructor_name == "Prof. Amit Verma"
    assert batch.enrolled_count == 0

    # 3. Create Student
    student = StudentController.create_student({
        "id_no": student_id_val,
        "name": "Rohit Kumar",
        "mobile_no": f"98765{uid[:5]}",
        "course_name": "Master in Architecture",
        "status": "Active",
        "assigned_staff_id": staff.id,
    })
    assert student.assigned_staff_id == staff.id

    # 4. Enroll Student in Batch
    enr = StaffController.enroll_student_in_batch(batch.id, student.id, remarks="Regular morning batch")
    assert enr is not None
    assert enr.status == "Active"

    # Reload batch and verify enrollment
    reloaded_batch = StaffController.get_batch_by_id(batch.id)
    assert reloaded_batch.enrolled_count == 1
    assert len(reloaded_batch.enrollments) == 1
    assert reloaded_batch.enrollments[0].student.name == "Rohit Kumar"

    # Verify Staff metrics & student count
    reloaded_staff = StaffController.get_staff_by_id(staff.id)
    assert reloaded_staff.active_batches_count == 1
    assert reloaded_staff.total_students_count == 1

    # 5. Remove Student from Batch
    removed = StaffController.remove_student_from_batch(batch.id, student.id)
    assert removed is True

    reloaded_batch_after = StaffController.get_batch_by_id(batch.id)
    assert reloaded_batch_after.enrolled_count == 0

    # Clean up
    StudentController.delete_student(student.id)
    StaffController.delete_batch(batch.id)
    StaffController.delete_staff(staff.id)


def test_staff_dashboard_metrics():
    metrics = StaffController.get_staff_dashboard_metrics()
    assert "total_staff" in metrics
    assert "active_staff" in metrics
    assert "total_batches" in metrics
    assert "active_batches" in metrics
    assert "active_enrollments" in metrics


def test_student_detail_view_with_staff_and_batch():
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication.instance() or QApplication(sys.argv)
    from app.modules.students.views.student_detail_view import StudentDetailView

    uid = uuid.uuid4().hex[:6]
    staff = StaffController.create_staff({
        "staff_id": f"STF-DV-{uid}",
        "name": "Prof. S. K. Gupta",
        "designation": "Civil HOD",
        "mobile_no": "9811122233",
        "status": "Active",
    })

    batch = StaffController.create_batch({
        "batch_code": f"BAT-DV-{uid}",
        "batch_name": "AutoCAD Masterclass",
        "staff_id": staff.id,
        "max_capacity": 20,
    })

    student = StudentController.create_student({
        "id_no": f"CD-DV-{uid}",
        "name": "Vikram Singh",
        "mobile_no": f"98765{uid[:5]}",
        "assigned_staff_id": staff.id,
        "total_fee": 20000.0,
        "net_fee": 20000.0,
    })

    StaffController.enroll_student_in_batch(batch.id, student.id)

    # 1. Fetch student and verify relations outside session
    fetched = StudentController.get_student_by_id(student.id)
    assert fetched is not None
    assert fetched.assigned_staff is not None
    assert fetched.assigned_staff.name == "Prof. S. K. Gupta"
    assert len(fetched.batches) == 1
    assert fetched.batches[0].batch_code == f"BAT-DV-{uid}"

    # 2. Instantiate StudentDetailView without error
    dlg = StudentDetailView(student_id=student.id)
    assert dlg is not None
    assert dlg.student.name == "Vikram Singh"

    # Clean up
    dlg.close()
    StudentController.delete_student(student.id)
    StaffController.delete_batch(batch.id)
    StaffController.delete_staff(staff.id)


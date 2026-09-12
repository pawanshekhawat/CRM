import pytest
import uuid
from app.core.database import init_db
from app.modules.courses.controllers import CourseController

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_db()

def test_default_courses_seeded():
    # Verify that standard courses catalog is populated
    courses = CourseController.get_all_courses()
    assert len(courses) >= 16

    # Verify key courses and their exact pricing
    arch = CourseController.get_course_by_name("Master Architecture")
    assert arch is not None
    assert arch.standard_fee == 120000.0
    assert arch.category == "Architecture & Civil"

    survey = CourseController.get_course_by_name("Land Survey")
    assert survey is not None
    assert survey.standard_fee == 70000.0

    dca = CourseController.get_course_by_name("DCA (Diploma in Computer Applications)")
    assert dca is not None
    assert dca.standard_fee == 35500.0

    fs = CourseController.get_course_by_name("Full Stack Web Development")
    assert fs is not None
    assert fs.standard_fee == 71000.0

    cnc = CourseController.get_course_by_name("Product Design & CNC Machine")
    assert cnc is not None
    assert cnc.standard_fee == 45500.0

    basic = CourseController.get_course_by_name("Basic Computer")
    assert basic is not None
    assert basic.standard_fee == 7500.0

def test_course_crud_lifecycle():
    uid = uuid.uuid4().hex[:6]
    c_name = f"Robotics & Mechatronics {uid}"

    # 1. Create Course
    course_data = {
        "course_code": f"CRS-ROB-{uid}",
        "name": c_name,
        "category": "Mechanical & Design",
        "standard_fee": 85000.0,
        "description": "ROS, Arduino, Embedded C, Motor Controllers & Kinematics",
        "status": "Active",
    }
    course = CourseController.create_course(course_data)
    assert course is not None
    assert course.id is not None
    assert course.name == c_name
    assert course.standard_fee == 85000.0

    # 2. Update Course
    updated = CourseController.update_course(course.id, {"standard_fee": 90000.0})
    assert updated is not None
    assert updated.standard_fee == 90000.0

    # 3. Retrieve
    retrieved = CourseController.get_course_by_id(course.id)
    assert retrieved is not None
    assert retrieved.name == c_name

    # 4. Delete Course
    deleted = CourseController.delete_course(course.id)
    assert deleted is True

def test_courses_dashboard_metrics():
    metrics = CourseController.get_courses_dashboard_metrics()
    assert "total_courses" in metrics
    assert "active_courses" in metrics
    assert "avg_fee" in metrics
    assert "categories_count" in metrics
    assert metrics["total_courses"] >= 16
    assert metrics["avg_fee"] > 0


def test_student_form_course_auto_fee():
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication.instance() or QApplication(sys.argv)
    from app.modules.students.views.student_form_dialog import StudentFormDialog

    dlg = StudentFormDialog()
    assert dlg.course_combo.count() > 0

    # Simulate selecting Master Architecture
    idx = dlg.course_combo.findData("Master Architecture")
    if idx < 0:
        for i in range(dlg.course_combo.count()):
            if "Master Architecture" in dlg.course_combo.itemText(i):
                idx = i
                break

    assert idx >= 0
    dlg.course_combo.setCurrentIndex(idx)
    assert dlg.total_fee_spin.value() == 120000.0
    assert dlg.net_fee_spin.value() == 120000.0

    dlg.close()


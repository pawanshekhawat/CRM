import pytest
from datetime import date
from app.core.database import init_db, get_db_session
from app.models.student import Student
from app.modules.students.controllers import StudentController
from app.modules.students.reports import ReportGenerator

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_student_crud_and_calculations():
    # 1. Test Custom Field Creation
    cf_blood = StudentController.save_custom_field_definition(
        field_label="Blood Group",
        field_type="select",
        options=["A+", "B+", "O+", "AB+"],
        is_required=False,
    )
    assert cf_blood.id is not None
    assert cf_blood.field_name == "blood_group"

    # 2. Test Student Creation with CADDESK Form Fields
    student_data = {
        "id_no": "CD-2026-TEST01",
        "is_online": True,
        "online_reg_no": "ONLINE-9988",
        "name": "Pawan Shekhawat",
        "father_name": "Rajendra Singh",
        "mother_name": "Sunita Kanwar",
        "dob": date(2001, 5, 15),
        "father_occupation": "Govt Service",
        "college_school": "Engineering College",
        "course_name": "Full Stack Development",
        "year_sem": "3rd Year",
        "aadhar_no": "123456789012",
        "mobile_no": "9876543210",
        "email": "pawan@example.com",
        "father_contact_no": "9876543211",
        "alternate_contact_no": "9876543212",
        "permanent_address": "Near Main Market, Sikar",
        "district": "Sikar",
        "state": "Rajasthan",
        "pin_code": "332001",
        "status": "Active",
        "admission_date": date.today(),
        "declaration_agreed": True,
        "total_fee": 25000.0,
        "discount_amount": 2000.0,
        "net_fee": 23000.0,
        "fee_remarks": "Special student discount applied",
    }

    # Course Sessions
    sessions_data = [
        {"course_name": "1st & 2nd-Session", "book_issued": True, "book_details": "Vol 1 Issued on 01/09/2026", "student_signed": True},
        {"course_name": "Web-Design, Graphic-Design", "book_issued": False, "book_details": "", "student_signed": False},
    ]

    # Installments (1st paid, 2nd scheduled)
    installments_data = [
        {"installment_no": 1, "installment_label": "1st", "due_amount": 10000.0, "paid_amount": 10000.0, "payment_mode": "UPI", "transaction_ref": "UPI12345678"},
        {"installment_no": 2, "installment_label": "2nd", "due_amount": 8000.0, "paid_amount": 0.0, "payment_mode": "Cash"},
        {"installment_no": 3, "installment_label": "3rd", "due_amount": 5000.0, "paid_amount": 0.0, "payment_mode": "Cash"},
    ]

    # Custom field value
    custom_vals = {
        cf_blood.id: "B+"
    }

    student = StudentController.create_student(
        student_data,
        sessions_data,
        installments_data,
        custom_vals,
    )

    assert student is not None
    assert student.id_no == "CD-2026-TEST01"
    assert student.name == "Pawan Shekhawat"
    assert student.net_fee == 23000.0
    assert student.total_paid == 10000.0
    assert student.balance_due == 13000.0
    assert student.fee_status == "Partial"
    assert len(student.course_sessions) == 2
    assert student.course_sessions[0].book_issued is True
    assert len(student.fee_installments) == 3

    # Check Custom field value
    retrieved_cf = StudentController.get_student_custom_values(student.id)
    assert retrieved_cf.get(cf_blood.id) == "B+"

    # 3. Test Search
    results = StudentController.get_all_students(search_query="Pawan")
    assert len(results) >= 1

    # 4. Test PDF Report Generation
    pdf_path = ReportGenerator.generate_admission_slip_pdf(student)
    assert pdf_path.endswith(".pdf")

    # 5. Test Excel Export
    excel_path = ReportGenerator.export_students_to_excel([student])
    assert excel_path.endswith(".xlsx")

    # 6. Cleanup
    deleted = StudentController.delete_student(student.id)
    assert deleted is True

def test_student_avatar_pixmap_generation():
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication.instance() or QApplication(sys.argv)
    from app.modules.students.views.student_list_view import create_student_avatar_pixmap
    
    # Test initials generation
    pix = create_student_avatar_pixmap(None, "Rajat Jangir", size=34)
    assert not pix.isNull()
    assert pix.width() == 34
    assert pix.height() == 34

    pix_single = create_student_avatar_pixmap(None, "Pawan", size=34)
    assert not pix_single.isNull()
    assert pix_single.width() == 34


def test_student_without_sessions_and_books():
    student_data = {
        "id_no": "CD-2026-NOSESS",
        "name": "Aman Sharma",
        "mobile_no": "9123456780",
        "course_name": "Python Development",
        "status": "Active",
        "total_fee": 15000.0,
        "discount_amount": 0.0,
        "net_fee": 15000.0,
    }
    installments = [
        {"installment_no": 1, "installment_label": "1st", "due_amount": 15000.0, "paid_amount": 15000.0, "payment_mode": "Cash"}
    ]
    student = StudentController.create_student(
        data=student_data,
        fee_installments_data=installments
    )
    assert student.id is not None
    assert student.name == "Aman Sharma"
    assert student.fee_status == "Paid"
    assert len(student.course_sessions) == 0

    # Test PDF & Excel generation
    pdf = ReportGenerator.generate_admission_slip_pdf(student)
    assert pdf.endswith(".pdf")

    excel = ReportGenerator.export_students_to_excel([student])
    assert excel.endswith(".xlsx")

    StudentController.delete_student(student.id)


def test_running_due_installments():
    student_data = {
        "id_no": "CD-TEST-RUNNING",
        "name": "Test Running Student",
        "mobile_no": "9876500001",
        "course_name": "CAD Testing",
        "status": "Active",
        "total_fee": 60000.0,
        "discount_amount": 0.0,
        "net_fee": 60000.0,
    }
    raw_installments = [
        {"installment_no": 1, "installment_label": "1st", "paid_amount": 5000.0, "payment_mode": "Cash"},
        {"installment_no": 2, "installment_label": "2nd", "paid_amount": 15000.0, "payment_mode": "Cash"},
        {"installment_no": 3, "installment_label": "3rd", "paid_amount": 10000.0, "payment_mode": "Cash"},
        {"installment_no": 4, "installment_label": "4th", "paid_amount": 0.0, "payment_mode": "Cash"},
    ]
    student = StudentController.create_student(
        data=student_data,
        fee_installments_data=raw_installments
    )
    assert student.id is not None
    assert len(student.fee_installments) == 4

    insts = student.fee_installments
    # 1st row: due = 60,000, paid = 5,000
    assert insts[0].due_amount == 60000.0
    assert insts[0].paid_amount == 5000.0
    assert insts[0].status == "Paid"

    # 2nd row: due = 55,000, paid = 15,000
    assert insts[1].due_amount == 55000.0
    assert insts[1].paid_amount == 15000.0
    assert insts[1].status == "Paid"

    # 3rd row: due = 40,000, paid = 10,000
    assert insts[2].due_amount == 40000.0
    assert insts[2].paid_amount == 10000.0
    assert insts[2].status == "Paid"

    # 4th row: due = 30,000, paid = 0
    assert insts[3].due_amount == 30000.0
    assert insts[3].paid_amount == 0.0
    assert insts[3].status == "Pending"

    # Total paid & balance
    assert student.total_paid == 30000.0
    assert student.balance_due == 30000.0
    assert student.fee_status == "Partial"

    StudentController.delete_student(student.id)




import pytest
from datetime import date
from app.core.database import init_db, get_db_session
from app.models.student import Student
from app.modules.students.controllers import StudentController
from app.modules.students.reports import ReportGenerator

@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    # Clean before test
    with get_db_session() as session:
        from app.models.custom_fields import CustomFieldDefinition, CustomFieldValue
        session.query(CustomFieldValue).delete()
        session.query(CustomFieldDefinition).delete()
        session.commit()
    yield
    # Clean after test
    with get_db_session() as session:
        from app.models.custom_fields import CustomFieldDefinition, CustomFieldValue
        session.query(CustomFieldValue).delete()
        session.query(CustomFieldDefinition).delete()
        session.query(Student).filter(Student.id_no.like("CD-2026-TEST%")).delete()
        session.commit()

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


def test_admission_form_viewer_and_status():
    from PySide6.QtWidgets import QApplication
    import sys
    import uuid
    app = QApplication.instance() or QApplication(sys.argv)
    from app.ui.widgets.form_image_viewer import FormImageViewer

    test_id_no = f"CD-TEST-{uuid.uuid4().hex[:6]}"

    # 1. Create student with admission form and Dropout status
    student_data = {
        "id_no": test_id_no,
        "name": "Test Form Student",
        "mobile_no": "9998887776",
        "course_name": "Master Architecture",
        "status": "Dropout",
        "total_fee": 120000.0,
        "discount_amount": 0.0,
        "net_fee": 120000.0,
        "admission_form_path": "form_CD-2026-0001.jpg",
    }
    student = StudentController.create_student(data=student_data)
    assert student.id is not None
    assert student.status == "Dropout"
    assert student.admission_form_path == "form_CD-2026-0001.jpg"

    try:
        # 2. Test FormImageViewer widget
        viewer = FormImageViewer(relative_form_path="form_CD-2026-0001.jpg", student_name=student.name)
        assert viewer.relative_path == "form_CD-2026-0001.jpg"
        viewer._zoom_in()
        viewer._zoom_out()
        viewer._actual_size()

        # 3. Test update status
        updated = StudentController.update_student(student.id, {"status": "Completed"})
        assert updated.status == "Completed"

        # 4. Test instant update_student_status method
        success = StudentController.update_student_status(student.id, "Active")
        assert success is True
        refetched = StudentController.get_student_by_id(student.id)
        assert refetched.status == "Active"

        # 5. Test StatusBadgeComboBox widget
        from app.modules.students.views.student_list_view import StatusBadgeComboBox
        changed_status = []
        combo = StatusBadgeComboBox(
            student_id=student.id,
            current_status=refetched.status,
            on_change_callback=lambda sid, nst: changed_status.append((sid, nst))
        )
        assert combo.currentText() == "Active"
        combo.setCurrentText("Dropout")
        assert len(changed_status) == 1
        assert changed_status[0] == (student.id, "Dropout")
    finally:
        # Clean up
        StudentController.delete_student(student.id)


def test_student_sorting_by_name_course_status():
    # Ensure test students exist
    s1 = StudentController.create_student({
        "id_no": "CD-SORT-A",
        "name": "Abhishek Verma",
        "mobile_no": "9111111111",
        "course_name": "AutoCAD",
        "status": "Active",
        "total_fee": 10000.0,
        "net_fee": 10000.0,
    })
    s2 = StudentController.create_student({
        "id_no": "CD-SORT-B",
        "name": "Zoya Khan",
        "mobile_no": "9222222222",
        "course_name": "Revit Architecture",
        "status": "Completed",
        "total_fee": 20000.0,
        "net_fee": 20000.0,
    })
    try:
        # 1. Test Sort by Name A-Z
        by_name_asc = StudentController.get_all_students(sort_by="Sort: Name (A-Z)")
        names_asc = [s.name.lower() for s in by_name_asc]
        assert names_asc == sorted(names_asc)

        # 2. Test Sort by Name Z-A
        by_name_desc = StudentController.get_all_students(sort_by="Sort: Name (Z-A)")
        names_desc = [s.name.lower() for s in by_name_desc]
        assert names_desc == sorted(names_desc, reverse=True)

        # 3. Test Sort by Course
        by_course = StudentController.get_all_students(sort_by="Sort: Courses")
        courses = [s.course_name or "" for s in by_course]
        assert courses == sorted(courses)

        # 4. Test Sort by Active Status (Active first)
        by_status = StudentController.get_all_students(sort_by="Sort: Active Status")
        status_order_map = {"Active": 1, "Completed": 2, "Dropout": 3}
        status_ranks = [status_order_map.get(s.status, 4) for s in by_status]
        assert status_ranks == sorted(status_ranks)
    finally:
        StudentController.delete_student(s1.id)
        StudentController.delete_student(s2.id)


def test_student_form_dialog_populate_aadhar_and_fields():
    from PySide6.QtWidgets import QApplication
    from app.modules.students.views.student_form_dialog import StudentFormDialog
    import sys
    app = QApplication.instance() or QApplication(sys.argv)

    student = StudentController.create_student({
        "id_no": "CD-TEST-DLG",
        "name": "Dialog Test Student",
        "aadhar_no": "999988887777",
        "mobile_no": "9333333333",
        "course_name": "Civil 3D",
        "status": "Active",
        "total_fee": 15000.0,
        "net_fee": 15000.0,
    })
    try:
        dlg = StudentFormDialog(student=student)
        assert dlg.id_input.text() == student.id_no
        assert dlg.name_input.text() == student.name
        if student.aadhar_no:
            assert dlg.aadhar_input.text() == student.aadhar_no
    finally:
        StudentController.delete_student(student.id)


def test_student_form_dialog_auto_default_and_dynamic_installments():
    from PySide6.QtWidgets import QApplication, QPushButton
    from app.modules.students.views.student_form_dialog import StudentFormDialog
    import sys
    app = QApplication.instance() or QApplication(sys.argv)

    dlg = StudentFormDialog()

    # 1. Verify all QPushButtons have autoDefault disabled (so Enter in inputs doesn't trigger photo upload)
    all_buttons = dlg.findChildren(QPushButton)
    assert len(all_buttons) > 0
    for btn in all_buttons:
        assert btn.autoDefault() is False, f"Button '{btn.text()}' has autoDefault=True, should be False!"
        assert btn.isDefault() is False, f"Button '{btn.text()}' has isDefault=True, should be False!"

    # 2. Verify initial 10 installment rows
    assert dlg.inst_table.rowCount() == 10
    assert dlg.inst_table.item(0, 0).text().strip() == "1st"
    assert dlg.inst_table.item(9, 0).text().strip() == "10th"

    # 3. Test dynamic addition of 11th and 12th installment rows
    dlg._on_add_installment_clicked()
    assert dlg.inst_table.rowCount() == 11
    assert dlg.inst_table.item(10, 0).text().strip() == "11th"

    dlg._on_add_installment_clicked()
    assert dlg.inst_table.rowCount() == 12
    assert dlg.inst_table.item(11, 0).text().strip() == "12th"

    # 4. Test ordinal label generator helper
    assert dlg._get_ordinal_label(0) == "1st"
    assert dlg._get_ordinal_label(1) == "2nd"
    assert dlg._get_ordinal_label(2) == "3rd"
    assert dlg._get_ordinal_label(10) == "11th"
    assert dlg._get_ordinal_label(20) == "21st"
    assert dlg._get_ordinal_label(21) == "22nd"
    assert dlg._get_ordinal_label(22) == "23rd"
    assert dlg._get_ordinal_label(23) == "24th"

    # 5. Test dynamic summary calculation with new rows
    dlg.net_fee_spin.setValue(100000.0)
    # Put 10,000 in row 10 (11th installment)
    paid_spin_11 = dlg.inst_table.cellWidget(10, 2)
    paid_spin_11.setValue(10000.0)
    assert "₹10,000.00" in dlg.total_paid_badge.text()
    assert "₹90,000.00" in dlg.balance_badge.text()


def test_status_badge_combo_box_style_and_dimensions():
    from PySide6.QtWidgets import QApplication
    from app.modules.students.views.student_list_view import StatusBadgeComboBox
    import sys
    app = QApplication.instance() or QApplication(sys.argv)

    combo = StatusBadgeComboBox(student_id="test_id", current_status="Active", on_change_callback=None)
    assert combo.height() == 28 or combo.maximumHeight() == 28
    sheet = combo.styleSheet()
    assert "padding: 0px 24px 0px 14px;" in sheet
    assert "margin: 0px;" in sheet
    assert "border-radius: 14px;" in sheet


def test_student_referral_lifecycle_and_commission():
    from PySide6.QtWidgets import QApplication
    from app.modules.students.views.student_form_dialog import StudentFormDialog
    from app.modules.students.views.student_detail_view import StudentDetailView
    import sys
    import uuid
    app = QApplication.instance() or QApplication(sys.argv)

    uid = uuid.uuid4().hex[:6]
    id_ref = f"CD-REF-A-{uid}"
    id_stud_b = f"CD-REF-B-{uid}"
    id_stud_c = f"CD-REF-C-{uid}"

    # 1. Create Referrer Student A
    student_a = StudentController.create_student({
        "id_no": id_ref,
        "name": "Referrer Student A",
        "mobile_no": "9811110001",
        "course_name": "Full Stack Development",
        "status": "Active",
        "total_fee": 50000.0,
        "discount_amount": 0.0,
        "net_fee": 50000.0,
    })
    assert student_a is not None

    try:
        # 2. Create Referred Student B (with 4000 discount and 2500 commission)
        student_b = StudentController.create_student({
            "id_no": id_stud_b,
            "name": "Referred Student B",
            "mobile_no": "9811110002",
            "course_name": "Master Architecture",
            "status": "Active",
            "total_fee": 80000.0,
            "discount_amount": 4000.0,
            "net_fee": 76000.0,
            "referred_by_student_id": student_a.id,
            "referral_discount": 4000.0,
            "referral_commission": 2500.0,
        })
        assert student_b is not None
        assert student_b.referred_by_student_id == student_a.id

        # 3. Create Referred Student C (with 5000 discount and 3000 commission)
        student_c = StudentController.create_student({
            "id_no": id_stud_c,
            "name": "Referred Student C",
            "mobile_no": "9811110003",
            "course_name": "AutoCAD Mechanical",
            "status": "Active",
            "total_fee": 40000.0,
            "discount_amount": 5000.0,
            "net_fee": 35000.0,
            "referred_by_student_id": student_a.id,
            "referral_discount": 5000.0,
            "referral_commission": 3000.0,
        })
        assert student_c is not None

        # 4. Fetch Referrer A and verify metrics & relationships
        refetched_a = StudentController.get_student_by_id(student_a.id)
        assert refetched_a.referrals_count == 2
        assert refetched_a.total_referral_commission_earned == 5500.0
        assert refetched_a.total_referral_discounts_given == 9000.0

        # Verify get_student_referrals query
        referrals_list = StudentController.get_student_referrals(student_a.id)
        assert len(referrals_list) == 2
        ref_ids = {r.id for r in referrals_list}
        assert student_b.id in ref_ids
        assert student_c.id in ref_ids

        # 5. Test StudentFormDialog auto-apply discount on referrer selection
        form_dlg = StudentFormDialog()
        # Find index for student A in combo
        idx_a = -1
        for i in range(form_dlg.referrer_combo.count()):
            if form_dlg.referrer_combo.itemData(i) == student_a.id:
                idx_a = i
                break
        assert idx_a > 0
        form_dlg.referrer_combo.setCurrentIndex(idx_a)
        # Should auto-populate default 4000 referral discount
        assert form_dlg.referral_discount_spin.value() == 4000.0
        assert form_dlg.discount_spin.value() >= 4000.0

        # 6. Test StudentDetailView with Referrals tab
        detail_view = StudentDetailView(student_id=student_a.id)
        assert detail_view.student.referrals_count == 2
        # Tab title should contain "(2)"
        tab_widget = detail_view.findChild(type(detail_view.main_layout.itemAt(1).widget()))
        tab_titles = [tab_widget.tabText(i) for i in range(tab_widget.count())] if tab_widget else []
        assert any("Referrals & Commission (2)" in t for t in tab_titles)

    finally:
        StudentController.delete_student(student_b.id)
        StudentController.delete_student(student_c.id)
        StudentController.delete_student(student_a.id)


def test_student_authentic_fee_preservation():
    """Verify that student total_fee and net_fee accurately preserve form amounts."""
    # 1. Create student with authentic AutoCAD course fee 14500
    student = StudentController.create_student({
        "id_no": "CD-FEE-TEST-01",
        "name": "Fee Test Student",
        "mobile_no": "9000000001",
        "course_name": "AutoCAD",
        "total_fee": 14500.0,
        "discount_amount": 0.0,
        "net_fee": 14500.0,
    })
    try:
        assert student.course_name == "AutoCAD"
        assert student.total_fee == 14500.0
        assert student.discount_amount == 0.0
        assert student.net_fee == 14500.0

        # 2. Update student to Master Architecture with authentic fee 25000
        updated = StudentController.update_student(
            student.id,
            data={"course_name": "Master Architecture", "total_fee": 25000.0, "discount_amount": 0.0, "net_fee": 25000.0}
        )
        assert updated.course_name == "Master Architecture"
        assert updated.total_fee == 25000.0
        assert updated.discount_amount == 0.0
        assert updated.net_fee == 25000.0
    finally:
        StudentController.delete_student(student.id)


def test_last_fee_paid_calculation_and_table_column():
    """Verify last fee paid date, days passed, sorting, and UI table column next to course enrolled."""
    from datetime import date, timedelta
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication.instance() or QApplication(sys.argv)
    from app.modules.students.views.student_list_view import StudentListView

    d1 = date.today() - timedelta(days=40)
    d2 = date.today() - timedelta(days=10)

    # 1. Student with multiple paid installments
    st_paid = StudentController.create_student(
        data={
            "id_no": "CD-2026-TEST-LP1",
            "name": "Last Paid Test Student",
            "mobile_no": "9998887771",
            "course_name": "Land Survey",
            "total_fee": 25000.0,
            "net_fee": 25000.0,
            "admission_date": d1,
        },
        fee_installments_data=[
            {"installment_no": 1, "installment_label": "1st", "due_amount": 10000.0, "paid_amount": 10000.0, "payment_date": d1},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 15000.0, "paid_amount": 15000.0, "payment_date": d2},
        ],
    )

    # 2. Student with no paid installments
    st_unpaid = StudentController.create_student(
        data={
            "id_no": "CD-2026-TEST-LP2",
            "name": "Unpaid Test Student",
            "mobile_no": "9998887772",
            "course_name": "AutoCAD",
            "total_fee": 15000.0,
            "net_fee": 15000.0,
            "admission_date": d1,
        },
        fee_installments_data=[
            {"installment_no": 1, "installment_label": "1st", "due_amount": 15000.0, "paid_amount": 0.0},
        ],
    )

    try:
        # Check model properties
        assert st_paid.latest_paid_installment is not None
        assert st_paid.latest_paid_installment.installment_no == 2
        assert st_paid.last_payment_date == d2
        assert st_paid.days_since_last_payment == 10
        assert "10d ago" in st_paid.last_payment_summary

        assert st_unpaid.latest_paid_installment is None
        assert st_unpaid.last_payment_date is None
        assert st_unpaid.days_since_last_payment is None
        assert st_unpaid.last_payment_summary == "No Payment"

        # Check sorting by last paid
        sorted_recent = StudentController.get_all_students(sort_by="Sort: Last Paid (Recent)")
        assert len(sorted_recent) >= 2
        # st_paid should appear before st_unpaid in recent paid sort
        paid_idx = next(i for i, s in enumerate(sorted_recent) if s.id == st_paid.id)
        unpaid_idx = next(i for i, s in enumerate(sorted_recent) if s.id == st_unpaid.id)
        assert paid_idx < unpaid_idx

        # Check UI table structure
        list_view = StudentListView()
        assert list_view.table.columnCount() == 7
        assert list_view.table.horizontalHeaderItem(2).text() == "Course Enrolled"
        assert list_view.table.horizontalHeaderItem(3).text() == "Last Fee Paid"
        assert list_view.table.horizontalHeaderItem(4).text() == "Fee Status"

        list_view.close()
    finally:
        StudentController.delete_student(st_paid.id)
        StudentController.delete_student(st_unpaid.id)




from datetime import date, timedelta
import pytest
from PySide6.QtWidgets import QApplication
import sys

from app.core.database import init_db, get_db_session
from app.models.message_template import MessageTemplate
from app.modules.messaging.controllers import MessageController
from app.modules.messaging.messaging_module import MessagingModule
from app.modules.messaging.views.messaging_view import MessagingView
from app.modules.messaging.views.template_editor_dialog import TemplateEditorDialog
from app.modules.messaging.views.dispatch_queue_dialog import DispatchQueueDialog
from app.modules.students.controllers import StudentController


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_db()


def test_default_templates_seeded_and_crud():
    # 1. Verify default templates seeded
    templates = MessageController.get_all_templates()
    assert len(templates) >= 5
    fee_tmpl = next((t for t in templates if "Fee Reminder" in t.title), None)
    assert fee_tmpl is not None
    assert "{balance_due}" in fee_tmpl.content

    # 2. Create custom template
    new_tmpl = MessageController.create_template({
        "title": "Test Custom Notification",
        "category": "Exams",
        "content": "Hello {name}, your CAD project is due next week.",
    })
    assert new_tmpl.id is not None
    assert new_tmpl.title == "Test Custom Notification"

    # 3. Update template
    updated = MessageController.update_template(new_tmpl.id, {
        "title": "Updated CAD Project Notification",
        "content": "Respected {name}, your CAD project deadline is Friday.",
    })
    assert updated.title == "Updated CAD Project Notification"

    # 4. Delete template
    deleted = MessageController.delete_template(new_tmpl.id)
    assert deleted is True


def test_spintax_and_variable_rendering():
    # Test Spintax resolution
    spintax_text = "{Dear|Hello|Respected} student, {welcome to class|greetings}!"
    resolved = MessageController.resolve_spintax(spintax_text)
    assert any(g in resolved for g in ["Dear", "Hello", "Respected"])
    assert any(w in resolved for w in ["welcome to class", "greetings"])
    assert "{" not in resolved and "}" not in resolved

    # Create dummy student for rendering
    d1 = date.today() - timedelta(days=25)
    st = StudentController.create_student(
        data={
            "id_no": "CD-MSG-TEST-01",
            "name": "Arjun Sharma",
            "mobile_no": "9876543210",
            "course_name": "Full Stack Web Development",
            "total_fee": 30000.0,
            "net_fee": 30000.0,
            "admission_date": d1,
        },
        fee_installments_data=[
            {"installment_no": 1, "installment_label": "1st", "due_amount": 10000.0, "paid_amount": 10000.0, "payment_date": d1},
        ],
    )

    try:
        template_str = "Hello {name} ({id_no}), your balance for {course} is ₹{balance_due}. Last paid on {last_paid_date} ({days_ago} days ago)."
        rendered = MessageController.render_message(template_str, st, randomize_spintax=True)

        assert "Arjun Sharma" in rendered
        assert "CD-MSG-TEST-01" in rendered
        assert "Full Stack Web Development" in rendered
        assert "20,000" in rendered  # balance due
        assert "25 days ago" in rendered
    finally:
        StudentController.delete_student(st.id)


def test_phone_normalization_and_whatsapp_urls():
    # 10-digit Indian number
    phone_10 = "9876543210"
    url_desktop = MessageController.build_whatsapp_url(phone_10, "Hello World", use_desktop_app=True)
    assert url_desktop.startswith("whatsapp://send?phone=919876543210&text=Hello%20World")

    url_web = MessageController.build_whatsapp_url(phone_10, "Fee Reminder ₹5,000", use_desktop_app=False)
    assert url_web.startswith("https://web.whatsapp.com/send?phone=919876543210")
    assert "5%2C000" in url_web or "5,000" in url_web or "%E2%82%B9" in url_web


def test_messaging_module_and_views():
    app = QApplication.instance() or QApplication(sys.argv)

    # 1. Module properties
    mod = MessagingModule()
    assert mod.module_id == "messaging"
    assert mod.module_name == "Message Automation"
    assert mod.module_icon == "📢"

    # 2. Instantiate MessagingView
    view = mod.create_widget()
    assert isinstance(view, MessagingView)
    assert view.table.columnCount() == 6
    assert view.template_combo.count() >= 5

    # 3. Test selection helpers
    view._select_all_visible()
    assert len(view.selected_student_ids) == len(view.filtered_students)

    view._deselect_all()
    assert len(view.selected_student_ids) == 0

    # 4. Instantiate TemplateEditorDialog
    t_dlg = TemplateEditorDialog(parent=view)
    assert t_dlg is not None
    t_dlg.close()

    # 5. Instantiate DispatchQueueDialog if students exist
    if view.all_students:
        q_dlg = DispatchQueueDialog(students=[view.all_students[0]], template_text="Hello {name}", parent=view)
        assert q_dlg.total_count == 1
        q_dlg.close()

    view.close()

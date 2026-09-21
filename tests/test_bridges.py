import pytest
from app.core.database import init_db
from app.bridge.crm_bridge import CRMBridge
from app.bridge.students_bridge import StudentsBridge
from app.bridge.courses_bridge import CoursesBridge
from app.bridge.staff_bridge import StaffBridge
from app.bridge.finance_bridge import FinanceBridge
from app.bridge.messaging_bridge import MessagingBridge
from app.bridge.reports_bridge import ReportsBridge
from app.bridge.updater_bridge import UpdaterBridge


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db()


def test_crm_bridge_properties_and_navigation():
    bridge = CRMBridge()
    assert "Personal CRM" in bridge.getAppName()
    assert bridge.getAppVersion() is not None
    assert bridge.getOrganizationName() == "CADDESK Centre"

    bridge.navigateTo("Students")
    assert bridge.getCurrentPage() == "Students"

    stats = bridge.getGlobalStats()
    assert isinstance(stats, dict)
    assert "total_students" in stats
    assert "total_courses" in stats


def test_students_bridge_crud_and_serialization():
    bridge = StudentsBridge()
    students = bridge.getStudents("", "All", "All", "All", "id_no")
    assert isinstance(students, list)
    assert len(students) > 0
    s0 = students[0]
    assert "name" in s0
    assert "id_no" in s0
    assert "net_payable_fee" in s0
    assert "balance_due" in s0
    assert "installments" in s0

    # Test updateStudentStatus slot
    orig_status = s0.get("status", "Active")
    success = bridge.updateStudentStatus(s0["id"], "Dropout")
    assert success is True
    updated = bridge.getStudentById(s0["id"])
    assert updated["status"] == "Dropout"

    # Revert back
    bridge.updateStudentStatus(s0["id"], orig_status)


def test_courses_bridge_crud_and_metrics():
    bridge = CoursesBridge()
    courses = bridge.getCourses()
    assert isinstance(courses, list)

    metrics = bridge.getMetrics()
    assert isinstance(metrics, dict)
    assert "total_courses" in metrics

    fee = bridge.getStandardFeeForCourse("Master Architecture")
    assert fee > 0

    code = bridge.generateCourseCode("Architecture & Civil")
    assert code.startswith("CRS-ARCH")


def test_staff_bridge_and_batches():
    bridge = StaffBridge()
    staff_list = bridge.getStaffList()
    assert isinstance(staff_list, list)

    batches = bridge.getBatches()
    assert isinstance(batches, list)

    metrics = bridge.getMetrics()
    assert "total_staff" in metrics
    assert "total_batches" in metrics


def test_finance_bridge_metrics_and_ledger():
    bridge = FinanceBridge()
    metrics = bridge.getFinanceMetrics()
    assert isinstance(metrics, dict)
    assert "total_collected" in metrics
    assert "total_outstanding" in metrics

    txs = bridge.getTransactions()
    assert isinstance(txs, list)

    dues = bridge.getOutstandingList()
    assert isinstance(dues, list)


def test_messaging_bridge_templates_and_spintax():
    bridge = MessagingBridge()
    templates = bridge.getTemplates()
    assert isinstance(templates, list)
    assert len(templates) > 0

    preview = bridge.previewMessage("{Hello|Dear} {name}, balance: ₹{balance_due}")
    assert isinstance(preview, str)
    assert "{" not in preview or "|" not in preview


def test_reports_bridge_document_list():
    bridge = ReportsBridge()
    docs = bridge.getDocumentList()
    assert isinstance(docs, list)

    st_list = bridge.getStudentsList()
    assert isinstance(st_list, list)
    if len(st_list) > 0:
        first_st = st_list[0]
        assert "name" in first_st
        assert "balance_due" in first_st


def test_updater_bridge_version():
    bridge = UpdaterBridge()
    ver = bridge.getCurrentVersion()
    assert ver is not None

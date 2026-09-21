from app.bridge.crm_bridge import CRMBridge
from app.bridge.students_bridge import StudentsBridge
from app.bridge.courses_bridge import CoursesBridge
from app.bridge.staff_bridge import StaffBridge
from app.bridge.finance_bridge import FinanceBridge
from app.bridge.messaging_bridge import MessagingBridge
from app.bridge.reports_bridge import ReportsBridge
from app.bridge.updater_bridge import UpdaterBridge

__all__ = [
    "CRMBridge",
    "StudentsBridge",
    "CoursesBridge",
    "StaffBridge",
    "FinanceBridge",
    "MessagingBridge",
    "ReportsBridge",
    "UpdaterBridge",
]

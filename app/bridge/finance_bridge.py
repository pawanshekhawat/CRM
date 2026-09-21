import logging
from datetime import datetime, date
from typing import Any, Dict, List, Optional
from sqlalchemy import func

from PySide6.QtCore import QObject, Signal, Slot

from app.core.database import get_db_session
from app.models.student import Student, StudentFeeInstallment
from app.modules.students.controllers import StudentController

logger = logging.getLogger("CRM.FinanceBridge")


class FinanceBridge(QObject):
    """Bridge for Finance, Fees, Transactions Ledger, and Outstanding Balances."""

    financeChanged = Signal()

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

    @Slot(result="QVariantMap")
    def getFinanceMetrics(self) -> Dict[str, Any]:
        """Calculates comprehensive financial overview."""
        with get_db_session() as session:
            try:
                today = date.today()
                students = session.query(Student).all()

                total_enrolled = len(students)
                net_fees_total = sum(s.effective_net_fee for s in students)
                total_collected = sum(s.total_paid for s in students)
                total_outstanding = sum(s.balance_due for s in students)

                # Today's collection
                today_collected = session.query(func.sum(StudentFeeInstallment.paid_amount)).filter(
                    StudentFeeInstallment.payment_date == today
                ).scalar() or 0.0

                # Overdue count and amount
                overdue_query = session.query(StudentFeeInstallment).filter(
                    StudentFeeInstallment.due_date < today,
                    StudentFeeInstallment.paid_amount < StudentFeeInstallment.due_amount,
                )
                overdue_count = overdue_query.count()
                overdue_amount = sum(float(i.due_amount - i.paid_amount) for i in overdue_query.all())

                # Status counts
                paid_students = sum(1 for s in students if s.fee_status == "Paid")
                partial_students = sum(1 for s in students if s.fee_status == "Partial")
                pending_students = sum(1 for s in students if s.fee_status in ("Pending", "No Fee"))

                return {
                    "net_fees_total": float(net_fees_total),
                    "total_collected": float(total_collected),
                    "total_outstanding": float(total_outstanding),
                    "today_collected": float(today_collected),
                    "overdue_count": overdue_count,
                    "overdue_amount": float(overdue_amount),
                    "total_students": total_enrolled,
                    "paid_students": paid_students,
                    "partial_students": partial_students,
                    "pending_students": pending_students,
                }
            except Exception as e:
                logger.error(f"Error calculating finance metrics: {e}")
                return {
                    "net_fees_total": 0.0,
                    "total_collected": 0.0,
                    "total_outstanding": 0.0,
                    "today_collected": 0.0,
                    "overdue_count": 0,
                    "overdue_amount": 0.0,
                    "total_students": 0,
                    "paid_students": 0,
                    "partial_students": 0,
                    "pending_students": 0,
                }

    @Slot(result="QVariantList")
    @Slot(str, result="QVariantList")
    @Slot(str, str, result="QVariantList")
    def getTransactions(self, search: str = "", mode_filter: str = "All") -> List[Dict[str, Any]]:
        """Fetches flat list of all recorded payment transactions with student details."""
        with get_db_session() as session:
            try:
                query = session.query(StudentFeeInstallment).join(Student).filter(
                    StudentFeeInstallment.paid_amount > 0
                )

                if mode_filter and mode_filter != "All":
                    query = query.filter(StudentFeeInstallment.payment_mode == mode_filter)

                if search:
                    term = f"%{search.strip()}%"
                    query = query.filter(
                        (Student.name.ilike(term)) |
                        (Student.id_no.ilike(term)) |
                        (StudentFeeInstallment.transaction_ref.ilike(term)) |
                        (Student.course_name.ilike(term))
                    )

                installments = query.order_by(StudentFeeInstallment.payment_date.desc()).limit(150).all()

                transactions = []
                for inst in installments:
                    s = inst.student
                    transactions.append({
                        "installment_id": str(inst.id),
                        "student_id": str(s.id) if s else "",
                        "student_name": s.name if s else "Unknown",
                        "student_id_no": s.id_no if s else "",
                        "course_name": s.course_name if s else "",
                        "installment_no": inst.installment_no,
                        "paid_amount": float(inst.paid_amount or 0.0),
                        "due_amount": float(inst.due_amount or 0.0),
                        "payment_date": inst.payment_date.strftime("%d %b %Y") if inst.payment_date else "",
                        "payment_mode": inst.payment_mode or "Cash",
                        "receipt_no": inst.transaction_ref or f"REC-{str(inst.id)[:6]}",
                        "remarks": inst.remarks or "",
                    })
                return transactions
            except Exception as e:
                logger.error(f"Error fetching transactions: {e}")
                return []

    @Slot(result="QVariantList")
    @Slot(str, result="QVariantList")
    @Slot(str, str, result="QVariantList")
    def getOutstandingList(self, search: str = "", course_filter: str = "All") -> List[Dict[str, Any]]:
        """Fetches list of students with outstanding dues."""
        with get_db_session() as session:
            try:
                query = session.query(Student).filter(Student.status == "Active")

                if course_filter and course_filter != "All":
                    query = query.filter(Student.course_name == course_filter)

                if search:
                    term = f"%{search.strip()}%"
                    query = query.filter(
                        (Student.name.ilike(term)) |
                        (Student.id_no.ilike(term)) |
                        (Student.mobile_no.ilike(term)) |
                        (Student.course_name.ilike(term))
                    )

                students = query.all()

                results = []
                for s in students:
                    if s.balance_due <= 0:
                        continue

                    last_paid = ""
                    days_ago = -1
                    if s.fee_installments:
                        paid_insts = [i for i in s.fee_installments if i.paid_amount > 0 and i.payment_date]
                        if paid_insts:
                            latest = max(paid_insts, key=lambda x: x.payment_date or date.min)
                            if latest and latest.payment_date:
                                last_paid = latest.payment_date.strftime("%d %b %Y")
                                days_ago = (date.today() - latest.payment_date).days

                    results.append({
                        "student_id": s.id,
                        "id_no": s.id_no or "",
                        "name": s.name or "",
                        "mobile_no": s.mobile_no or "",
                        "course_name": s.course_name or "",
                        "total_fee": float(s.effective_net_fee or 0.0),
                        "total_paid": float(s.total_paid or 0.0),
                        "balance_due": float(s.balance_due or 0.0),
                        "fee_status": s.fee_status or "Pending",
                        "last_paid_date": last_paid,
                        "days_ago": days_ago,
                    })
                return sorted(results, key=lambda x: x["balance_due"], reverse=True)
            except Exception as e:
                logger.error(f"Error fetching outstanding list: {e}")
                return []

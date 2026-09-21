import json
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl

from app.core.config import DATA_DIR, PHOTOS_DIR, RECEIPTS_DIR, EXPORTS_DIR, ADMISSION_FORMS_DIR
from app.modules.students.controllers import StudentController
from app.modules.students.reports import ReportGenerator
from app.models.custom_fields import CustomFieldDefinition

logger = logging.getLogger("CRM.StudentsBridge")


def serialize_student(student: Any) -> Dict[str, Any]:
    """Serializes a Student model into a clean dictionary suitable for QML models."""
    if not student:
        return {}

    # Calculate last fee paid date and days ago
    last_paid_date_str = ""
    days_ago = None
    days_ago_str = "No payment yet"
    if getattr(student, "fee_installments", None):
        paid_installments = [i for i in student.fee_installments if (getattr(i, 'paid_amount', 0) or 0) > 0 and getattr(i, 'payment_date', None)]
        if paid_installments:
            latest_inst = max(paid_installments, key=lambda x: x.payment_date or date.min)
            if latest_inst and latest_inst.payment_date:
                last_paid_date_str = latest_inst.payment_date.strftime("%d %b %Y")
                days_ago = (date.today() - latest_inst.payment_date).days
                if days_ago == 0:
                    days_ago_str = "Today"
                elif days_ago == 1:
                    days_ago_str = "Yesterday"
                else:
                    days_ago_str = f"{days_ago} days ago"

    # Serialize installments
    installments_list = []
    if getattr(student, "fee_installments", None):
        for inst in sorted(student.fee_installments, key=lambda x: getattr(x, 'installment_no', 0)):
            paid_amt = float(getattr(inst, 'paid_amount', 0.0) or 0.0)
            due_amt = float(getattr(inst, 'due_amount', 0.0) or 0.0)
            inst_status = getattr(inst, 'status', '') or ("Paid" if paid_amt >= due_amt and due_amt > 0 else ("Partial" if paid_amt > 0 else "Pending"))
            installments_list.append({
                "id": str(getattr(inst, 'id', '')),
                "installment_no": getattr(inst, 'installment_no', 1),
                "installment_label": getattr(inst, 'installment_label', '') or f"{getattr(inst, 'installment_no', 1)}th",
                "due_amount": due_amt,
                "paid_amount": paid_amt,
                "due_date": inst.due_date.strftime("%Y-%m-%d") if getattr(inst, 'due_date', None) else "",
                "payment_date": inst.payment_date.strftime("%Y-%m-%d") if getattr(inst, 'payment_date', None) else "",
                "payment_mode": getattr(inst, 'payment_mode', '') or "Cash",
                "receipt_no": getattr(inst, 'transaction_ref', '') or f"REC-{str(getattr(inst, 'id', ''))[:6]}",
                "remarks": getattr(inst, 'remarks', '') or "",
                "status": inst_status,
            })

    # Serialize sessions & book records
    sessions_list = []
    if getattr(student, "course_sessions", None):
        for sess in sorted(student.course_sessions, key=lambda x: getattr(x, 'session_order', 0)):
            sessions_list.append({
                "id": str(getattr(sess, 'id', '')),
                "session_no": getattr(sess, 'session_order', 1),
                "session_name": getattr(sess, 'course_name', '') or f"Session {getattr(sess, 'session_order', 1)}",
                "faculty_name": "",
                "book_issued": bool(getattr(sess, 'book_issued', False)),
                "book_issue_date": "",
                "book_title": getattr(sess, 'book_details', '') or "",
                "student_signature": bool(getattr(sess, 'student_signed', False)),
            })

    # Custom field values
    custom_fields_dict = {}
    if hasattr(student, "custom_values") and student.custom_values:
        for cv in student.custom_values:
            if hasattr(cv, "definition") and cv.definition:
                custom_fields_dict[cv.definition.field_key] = cv.value

    # Assigned staff and batch info
    assigned_staff_name = student.assigned_staff.name if getattr(student, 'assigned_staff', None) else ""
    batch_names = [be.batch.batch_name for be in student.batch_enrollments if be and be.batch] if hasattr(student, "batch_enrollments") and student.batch_enrollments else []
    primary_batch = batch_names[0] if batch_names else ""

    # Photo URL
    photo_file = None
    if getattr(student, 'photo_path', None):
        p = PHOTOS_DIR / student.photo_path
        if p.exists():
            photo_file = p
    elif getattr(student, 'id_no', None):
        p = PHOTOS_DIR / f"{student.id_no}.jpg"
        if p.exists():
            photo_file = p
    photo_url = f"file:///{photo_file.as_posix()}" if photo_file and photo_file.exists() else ""

    # Scanned Physical Admission Form URL
    form_file = None
    if getattr(student, 'admission_form_path', None):
        p = ADMISSION_FORMS_DIR / student.admission_form_path
        if p.exists():
            form_file = p
        else:
            p_abs = Path(student.admission_form_path)
            if p_abs.exists():
                form_file = p_abs
    if not form_file and getattr(student, 'id_no', None):
        p = ADMISSION_FORMS_DIR / f"form_{student.id_no}.jpg"
        if p.exists():
            form_file = p
        else:
            p2 = ADMISSION_FORMS_DIR / f"{student.id_no}.jpg"
            if p2.exists():
                form_file = p2

    form_url = f"file:///{form_file.as_posix()}" if form_file and form_file.exists() else ""
    form_raw_path = str(form_file.resolve()) if form_file and form_file.exists() else ""

    total_course_fee = float(getattr(student, 'total_fee', 0.0) or 0.0)
    scholarship_discount = float(getattr(student, 'discount_amount', 0.0) or 0.0)
    net_payable_fee = float(getattr(student, 'effective_net_fee', 0.0) or getattr(student, 'net_fee', 0.0) or 0.0)
    total_paid_fee = float(getattr(student, 'total_paid', 0.0) or 0.0)
    balance_due = float(getattr(student, 'balance_due', 0.0) or 0.0)

    # Fee status display with balance amount
    fee_status = getattr(student, 'fee_status', 'Pending') or "Pending"
    if fee_status.lower() == "paid":
        fee_status_display = "Paid"
    elif fee_status.lower() == "partial":
        fee_status_display = f"Partial (Bal: ₹{int(balance_due):,})"
    else:
        fee_status_display = f"Pending (Bal: ₹{int(balance_due):,})" if balance_due > 0 else "Pending"

    return {
        "id": str(getattr(student, 'id', '')),
        "id_no": getattr(student, 'id_no', '') or "",
        "name": getattr(student, 'name', '') or "",
        "online_admission": bool(getattr(student, 'is_online', False)),
        "online_reference_no": getattr(student, 'online_reg_no', '') or "",
        "father_name": getattr(student, 'father_name', '') or "",
        "mother_name": getattr(student, 'mother_name', '') or "",
        "dob": student.dob.strftime("%Y-%m-%d") if getattr(student, 'dob', None) else "",
        "father_occupation": getattr(student, 'father_occupation', '') or "",
        "college_school": getattr(student, 'college_school', '') or "",
        "year_semester": getattr(student, 'year_sem', '') or "",
        "aadhar_no": getattr(student, 'aadhar_no', '') or "",
        "mobile_no": getattr(student, 'mobile_no', '') or "",
        "email": getattr(student, 'email', '') or "",
        "father_contact": getattr(student, 'father_contact_no', '') or "",
        "alternate_contact": getattr(student, 'alternate_contact_no', '') or "",
        "permanent_address": getattr(student, 'permanent_address', '') or "",
        "district": getattr(student, 'district', '') or "",
        "state": getattr(student, 'state', '') or "Rajasthan",
        "pin_code": getattr(student, 'pin_code', '') or "",
        "course_name": getattr(student, 'course_name', '') or "",
        "admission_date": student.admission_date.strftime("%Y-%m-%d") if getattr(student, 'admission_date', None) else "",
        "total_course_fee": total_course_fee,
        "scholarship_discount": scholarship_discount,
        "net_payable_fee": net_payable_fee,
        "total_paid_fee": total_paid_fee,
        "balance_due": balance_due,
        "fee_status": fee_status,
        "fee_status_display": fee_status_display,
        "status": getattr(student, 'status', 'Active') or "Active",
        "notes": getattr(student, 'fee_remarks', '') or "",
        "last_paid_date_str": last_paid_date_str or "—",
        "days_ago": days_ago if days_ago is not None else -1,
        "days_ago_str": days_ago_str,
        "photo_url": photo_url,
        "admission_form_url": form_url,
        "admission_form_raw_path": form_raw_path,
        "has_admission_form": bool(form_url),
        "assigned_staff_name": assigned_staff_name,
        "primary_batch": primary_batch,
        "batch_names": batch_names,
        "installments": installments_list,
        "course_sessions": sessions_list,
        "custom_fields": custom_fields_dict,
        "admission_form_pages_count": 1 if form_url else 0,
    }


class StudentsBridge(QObject):
    """Bridge for Student CRUD, Search, Multi-Filter, and Profile Actions."""

    studentsChanged = Signal()
    studentSaved = Signal(bool, str, str)  # success, message, student_id
    paymentRecorded = Signal(bool, str)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

    @Slot(result="QVariantList")
    @Slot(str, result="QVariantList")
    @Slot(str, str, result="QVariantList")
    @Slot(str, str, str, result="QVariantList")
    @Slot(str, str, str, str, result="QVariantList")
    @Slot(str, str, str, str, str, result="QVariantList")
    def getStudents(
        self,
        search: str = "",
        status: str = "All",
        course: str = "All",
        fee: str = "All",
        sort_by: str = "id_no",
    ) -> List[Dict[str, Any]]:
        """Fetch students with multi-filtering and return serialized list for QML DataTable."""
        try:
            students = StudentController.get_all_students(
                search_query=search if search and search.strip() else None,
                status_filter=status if status != "All" else None,
                course_filter=course if course != "All" else None,
                fee_filter=fee if fee != "All" else None,
                sort_by=sort_by or "id_no",
            )
            return [serialize_student(s) for s in students]
        except Exception as e:
            logger.error(f"Error fetching students: {e}", exc_info=True)
            return []

    @Slot(str, result="QVariantMap")
    @Slot("QVariant", result="QVariantMap")
    def getStudentById(self, student_id: Any) -> Dict[str, Any]:
        """Fetch detailed student profile by primary ID."""
        try:
            student = StudentController.get_student_by_id(str(student_id))
            return serialize_student(student)
        except Exception as e:
            logger.error(f"Error fetching student {student_id}: {e}", exc_info=True)
            return {}

    @Slot(str, result="QVariantMap")
    @Slot(str, str, result="QVariantMap")
    @Slot(str, str, "QVariantList", result="QVariantMap")
    def saveStudent(self, data_json: str, photo_path: str = "", form_paths: List[str] = None) -> Dict[str, Any]:
        """Creates or updates a student admission record."""
        try:
            data = json.loads(data_json)
            student_id = data.get("id")

            # Map alias names to DB model column names
            if "total_course_fee" in data and "total_fee" not in data:
                data["total_fee"] = data["total_course_fee"]
            if "scholarship_discount" in data and "discount_amount" not in data:
                data["discount_amount"] = data["scholarship_discount"]
            if "net_payable_fee" in data and "net_fee" not in data:
                data["net_fee"] = data["net_payable_fee"]
            if "father_contact" in data and "father_contact_no" not in data:
                data["father_contact_no"] = data["father_contact"]
            if "alternate_contact" in data and "alternate_contact_no" not in data:
                data["alternate_contact_no"] = data["alternate_contact"]
            if "year_semester" in data and "year_sem" not in data:
                data["year_sem"] = data["year_semester"]

            # Parse string dates to datetime.date objects
            for date_field in ["dob", "admission_date"]:
                if date_field in data and data[date_field]:
                    try:
                        data[date_field] = datetime.strptime(str(data[date_field])[:10], "%Y-%m-%d").date()
                    except Exception:
                        pass

            if "fee_installments" in data:
                for inst in data["fee_installments"]:
                    for df in ["due_date", "payment_date"]:
                        if df in inst and inst[df]:
                            try:
                                inst[df] = datetime.strptime(str(inst[df])[:10], "%Y-%m-%d").date()
                            except Exception:
                                pass

            if "course_sessions" in data:
                for sess in data["course_sessions"]:
                    if "book_issue_date" in sess and sess["book_issue_date"]:
                        try:
                            sess["book_issue_date"] = datetime.strptime(str(sess["book_issue_date"])[:10], "%Y-%m-%d").date()
                        except Exception:
                            pass

            clean_photo = photo_path if photo_path and Path(photo_path).exists() else None
            clean_forms = [p for p in (form_paths or []) if Path(p).exists()] if form_paths else None

            if student_id and str(student_id).strip() != "" and str(student_id) != "0":
                student = StudentController.update_student(
                    student_id=str(student_id),
                    data=data,
                    course_sessions_data=data.get("course_sessions"),
                    fee_installments_data=data.get("fee_installments"),
                )
                msg = f"Student {student.name} updated successfully."
                ret_id = str(student.id)
            else:
                student = StudentController.create_student(
                    data=data,
                    course_sessions_data=data.get("course_sessions"),
                    fee_installments_data=data.get("fee_installments"),
                )
                msg = f"Student {student.name} enrolled with ID {student.id_no}."
                ret_id = str(student.id)

            self.studentsChanged.emit()
            self.studentSaved.emit(True, msg, ret_id)
            return {"success": True, "message": msg, "id": ret_id}

        except Exception as e:
            logger.error(f"Error saving student: {e}", exc_info=True)
            self.studentSaved.emit(False, str(e), "")
            return {"success": False, "message": str(e), "id": ""}

    @Slot(str, str, result=bool)
    @Slot("QVariant", str, result=bool)
    def updateAdmissionForm(self, student_id: Any, file_path: str) -> bool:
        """Attaches or updates the scanned physical admission form image for a student."""
        try:
            clean_path = str(file_path or "")
            if clean_path.startswith("file:///"):
                clean_path = clean_path[8:]
            elif clean_path.startswith("file://"):
                clean_path = clean_path[7:]

            p = Path(clean_path)
            if not p.exists():
                logger.warning(f"Admission form file not found: {clean_path}")
                return False

            saved_name = StudentController.save_admission_form_attachment(str(p))
            if saved_name:
                StudentController.update_student(str(student_id), {"admission_form_path": saved_name})
                self.studentsChanged.emit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating admission form: {e}", exc_info=True)
            return False

    @Slot(str, str, result=bool)
    @Slot("QVariant", str, result=bool)
    def updateStudentStatus(self, student_id: Any, status: str) -> bool:
        """Instantly updates a student's active status (Active, Completed, Dropout)."""
        try:
            target_status = str(status or "Active").strip()
            # Normalize display terms
            if target_status.lower() in ("dropped", "dropout"):
                target_status = "Dropout"
            elif target_status.lower() == "completed":
                target_status = "Completed"
            elif target_status.lower() == "active":
                target_status = "Active"

            success = StudentController.update_student_status(str(student_id), target_status)
            if success:
                self.studentsChanged.emit()
            return success
        except Exception as e:
            logger.error(f"Error updating status for student {student_id}: {e}", exc_info=True)
            return False

    @Slot(str, result=bool)
    @Slot("QVariant", result=bool)
    def deleteStudent(self, student_id: Any) -> bool:
        """Deletes a student record."""
        try:
            success = StudentController.delete_student(str(student_id))
            if success:
                self.studentsChanged.emit()
            return success
        except Exception as e:
            logger.error(f"Error deleting student {student_id}: {e}", exc_info=True)
            return False

    @Slot(str, str, float, str, str, str, str, result="QVariantMap")
    @Slot("QVariant", "QVariant", float, str, str, str, str, result="QVariantMap")
    def recordPayment(
        self,
        student_id: Any,
        installment_id: Any = "",
        amount_paid: float = 0.0,
        payment_date: str = "",
        payment_mode: str = "Cash",
        receipt_no: str = "",
        remarks: str = "",
    ) -> Dict[str, Any]:
        """Records fee installment payment and recalculates balances."""
        try:
            p_date = None
            if payment_date:
                try:
                    p_date = datetime.strptime(str(payment_date)[:10], "%Y-%m-%d").date()
                except Exception:
                    p_date = date.today()
            else:
                p_date = date.today()

            student = StudentController.record_fee_payment(
                student_id=str(student_id),
                installment_id=str(installment_id) if installment_id else None,
                amount_paid=float(amount_paid),
                payment_date=p_date,
                payment_mode=payment_mode,
                receipt_no=receipt_no,
                remarks=remarks,
            )

            if not student:
                return {"success": False, "message": "Student record not found"}

            self.studentsChanged.emit()
            self.paymentRecorded.emit(True, f"Payment of ₹{amount_paid:,.2f} recorded for {student.name}.")
            return {"success": True, "message": "Payment recorded successfully", "student": serialize_student(student)}

        except Exception as e:
            logger.error(f"Error recording payment: {e}", exc_info=True)
            self.paymentRecorded.emit(False, str(e))
            return {"success": False, "message": str(e)}

    @Slot(str, result=str)
    @Slot("QVariant", result=str)
    def generateAdmissionPdf(self, student_id: Any) -> str:
        """Generates printable admission slip PDF."""
        try:
            student = StudentController.get_student_by_id(str(student_id))
            if not student:
                return ""
            pdf_path = ReportGenerator.generate_admission_slip_pdf(student)
            return pdf_path
        except Exception as e:
            logger.error(f"Error generating admission PDF: {e}", exc_info=True)
            return ""

    @Slot(str, str, result=str)
    @Slot("QVariant", "QVariant", result=str)
    def generateReceiptPdf(self, student_id: Any, installment_id: Any) -> str:
        """Generates official fee receipt PDF for a specific installment."""
        try:
            student = StudentController.get_student_by_id(str(student_id))
            if not student:
                return ""
            installment = next((i for i in student.fee_installments if str(i.id) == str(installment_id)), None)
            if not installment:
                return ""
            pdf_path = ReportGenerator.generate_fee_receipt_pdf(student, installment)
            return pdf_path
        except Exception as e:
            logger.error(f"Error generating receipt PDF: {e}", exc_info=True)
            return ""

    @Slot(result=str)
    @Slot(str, result=str)
    @Slot(str, str, result=str)
    @Slot(str, str, str, result=str)
    @Slot(str, str, str, str, result=str)
    def exportToExcel(
        self,
        search: str = "",
        status: str = "All",
        course: str = "All",
        fee: str = "All",
    ) -> str:
        """Exports filtered student records to Excel (.xlsx)."""
        try:
            students = StudentController.get_all_students(
                search_query=search if search and search.strip() else None,
                status_filter=status if status != "All" else None,
                course_filter=course if course != "All" else None,
                fee_filter=fee if fee != "All" else None,
            )
            excel_path = ReportGenerator.export_students_to_excel(students)
            return excel_path
        except Exception as e:
            logger.error(f"Error exporting students to Excel: {e}", exc_info=True)
            return ""

    @Slot(result="QVariantList")
    def getCustomFields(self) -> List[Dict[str, Any]]:
        """Retrieves active custom field definitions."""
        try:
            defs = StudentController.get_custom_field_definitions("student")
            return [
                {
                    "id": str(d.id),
                    "field_name": d.field_name,
                    "field_label": d.field_label,
                    "field_type": d.field_type,
                    "is_required": bool(d.is_required),
                }
                for d in defs
            ]
        except Exception:
            return []

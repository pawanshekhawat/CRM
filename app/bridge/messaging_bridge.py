import json
import logging
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl

from app.modules.messaging.controllers import MessageController
from app.modules.students.controllers import StudentController

logger = logging.getLogger("CRM.MessagingBridge")


def serialize_template(tmpl: Any) -> Dict[str, Any]:
    """Serializes a MessageTemplate model for QML."""
    if not tmpl:
        return {}
    return {
        "id": str(tmpl.id),
        "title": tmpl.title or "Untitled Template",
        "category": tmpl.category or "General",
        "content": tmpl.content or "",
        "is_default": bool(tmpl.is_default),
        "sort_order": int(tmpl.sort_order or 0),
    }


class MessagingBridge(QObject):
    """Bridge for WhatsApp Messaging, Templates CRUD, Merge Tags, and Recipient Targeting."""

    templatesChanged = Signal()
    templateSaved = Signal(bool, str, str)
    messageDispatched = Signal(bool, str)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

    @Slot(result="QVariantList")
    def getTemplates(self) -> List[Dict[str, Any]]:
        """Fetches all message templates."""
        try:
            templates = MessageController.get_all_templates()
            return [serialize_template(t) for t in templates]
        except Exception as e:
            logger.error(f"Error fetching templates: {e}")
            return []

    @Slot(str, result="QVariantMap")
    def getTemplateById(self, template_id: str) -> Dict[str, Any]:
        """Fetches a template by ID."""
        try:
            tmpl = MessageController.get_template_by_id(template_id)
            return serialize_template(tmpl)
        except Exception as e:
            logger.error(f"Error fetching template {template_id}: {e}")
            return {}

    @Slot(str, result="QVariantMap")
    def saveTemplate(self, data_json: str) -> Dict[str, Any]:
        """Creates or updates a message template."""
        try:
            data = json.loads(data_json)
            template_id = data.get("id")

            if template_id:
                tmpl = MessageController.update_template(template_id, data)
                if not tmpl:
                    return {"success": False, "message": "Template not found", "id": ""}
                msg = f"Template '{tmpl.title}' updated."
                ret_id = str(tmpl.id)
            else:
                tmpl = MessageController.create_template(data)
                msg = f"Template '{tmpl.title}' created."
                ret_id = str(tmpl.id)

            self.templatesChanged.emit()
            self.templateSaved.emit(True, msg, ret_id)
            return {"success": True, "message": msg, "id": ret_id}

        except Exception as e:
            logger.error(f"Error saving template: {e}")
            self.templateSaved.emit(False, str(e), "")
            return {"success": False, "message": str(e), "id": ""}

    @Slot(str, result=bool)
    def deleteTemplate(self, template_id: str) -> bool:
        """Deletes a message template."""
        try:
            success = MessageController.delete_template(template_id)
            if success:
                self.templatesChanged.emit()
            return success
        except Exception as e:
            logger.error(f"Error deleting template {template_id}: {e}")
            return False

    @Slot(str, result=str)
    @Slot(str, str, result=str)
    @Slot(str, int, result=str)
    @Slot(str, str, bool, result=str)
    @Slot(str, int, bool, result=str)
    @Slot(str, "QVariant", bool, result=str)
    def previewMessage(self, template_text: str, student_id: Any = 0, randomize_spintax: bool = True) -> str:
        """Renders preview text with live placeholders and Spintax resolution."""
        try:
            student = None
            if student_id and str(student_id).strip() != "" and str(student_id) != "0":
                student = StudentController.get_student_by_id(str(student_id))
            
            if not student:
                # Get first student with dues or active student
                students = StudentController.get_all_students(status_filter="Active")
                student = students[0] if students else None

            if student:
                return MessageController.render_message(template_text, student, randomize_spintax=randomize_spintax)

            # Fallback basic replacement
            resolved = MessageController.resolve_spintax(template_text) if randomize_spintax else template_text
            sample_map = {
                "{name}": "Shivkant Batu",
                "{first_name}": "Shivkant",
                "{id_no}": "CD-2026-0001",
                "{course}": "AutoCAD",
                "{balance_due}": "10,000",
                "{total_paid}": "25,000",
                "{total_fee}": "35,000",
                "{last_paid_date}": "01 Sep 2026",
                "{days_ago}": "15",
                "{admission_date}": "01 Jun 2026",
                "{mobile_no}": "9828965484",
                "{father_name}": "Mr. Batu",
            }
            for k, v in sample_map.items():
                resolved = resolved.replace(k, v)
            return resolved
        except Exception as e:
            logger.error(f"Error rendering message preview: {e}")
            return template_text

    @Slot(result="QVariantList")
    @Slot(str, result="QVariantList")
    @Slot(str, str, result="QVariantList")
    @Slot(str, str, str, result="QVariantList")
    def getRecipients(self, audience: str = "All", course_filter: str = "All", fee_filter: str = "All") -> List[Dict[str, Any]]:
        """
        Fetches targeted student list according to selected audience:
        - "All"
        - "Pending Fees" / "Overdue"
        - "Active"
        - "Course"
        """
        try:
            status_f = "Active" if audience in ("All", "Active", "Pending Fees") else None
            fee_f = "Pending" if audience == "Pending Fees" else (fee_filter if fee_filter != "All" else None)
            course_f = course_filter if course_filter != "All" else None

            students = StudentController.get_all_students(
                status_filter=status_f,
                fee_filter=fee_f,
                course_filter=course_f,
            )

            recipients = []
            for s in students:
                if not s.mobile_no:
                    continue
                
                # Calculate last payment info
                last_paid = ""
                days_ago = -1
                days_ago_str = "No payment yet"
                if getattr(s, "fee_installments", None):
                    paid_insts = [i for i in s.fee_installments if (getattr(i, 'paid_amount', 0) or 0) > 0 and getattr(i, 'payment_date', None)]
                    if paid_insts:
                        latest = max(paid_insts, key=lambda x: x.payment_date)
                        if latest and latest.payment_date:
                            last_paid = latest.payment_date.strftime("%d %b %Y")
                            from datetime import date
                            days_ago = (date.today() - latest.payment_date).days
                            days_ago_str = f"{days_ago} days ago"

                bal = float(getattr(s, 'balance_due', 0.0) or 0.0)
                fee_status = getattr(s, 'fee_status', 'Pending') or "Pending"
                fee_status_display = f"Partial (Bal: ₹{int(bal):,})" if fee_status.lower() == "partial" else (f"Pending (Bal: ₹{int(bal):,})" if bal > 0 else "Paid")

                recipients.append({
                    "id": str(s.id),
                    "id_no": s.id_no or "",
                    "name": s.name or "",
                    "mobile_no": s.mobile_no or "",
                    "course_name": s.course_name or "",
                    "balance_due": bal,
                    "fee_status": fee_status,
                    "fee_status_display": fee_status_display,
                    "last_paid_date_str": last_paid or "—",
                    "days_ago": days_ago,
                    "days_ago_str": days_ago_str,
                })
            return recipients
        except Exception as e:
            logger.error(f"Error fetching recipients: {e}")
            return []

    @Slot(str, str, bool, result=str)
    @Slot(int, str, bool, result=str)
    @Slot("QVariant", str, bool, result=str)
    def getWhatsAppUrlForStudent(self, student_id: Any, template_text: str, use_desktop_app: bool = True) -> str:
        """Builds ready-to-launch WhatsApp URL for a specific recipient."""
        try:
            student = StudentController.get_student_by_id(str(student_id))
            if not student or not student.mobile_no:
                return ""
            rendered = MessageController.render_message(template_text, student, randomize_spintax=True)
            url = MessageController.build_whatsapp_url(student.mobile_no, rendered, use_desktop_app=use_desktop_app)
            return url
        except Exception as e:
            logger.error(f"Error building WhatsApp URL: {e}")
            return ""

    @Slot(str, str, bool, result=bool)
    @Slot(str, str, result=bool)
    @Slot(int, str, bool, result=bool)
    @Slot(int, str, result=bool)
    @Slot("QVariant", str, bool, result=bool)
    @Slot("QVariant", str, result=bool)
    def sendWhatsAppToStudent(self, student_id: Any, template_text: str, use_desktop_app: bool = True) -> bool:
        """Launches WhatsApp directly with the customized student message."""
        try:
            student = StudentController.get_student_by_id(str(student_id))
            if not student or not student.mobile_no:
                self.messageDispatched.emit(False, "Student does not have a valid mobile number.")
                return False

            rendered = MessageController.render_message(template_text, student, randomize_spintax=True)
            return self.sendDirectWhatsApp(str(student_id), rendered)
        except Exception as e:
            logger.error(f"Error opening WhatsApp: {e}")
            self.messageDispatched.emit(False, str(e))
            return False

    @Slot(str, str, result=bool)
    @Slot(int, str, result=bool)
    @Slot("QVariant", str, result=bool)
    def sendDirectWhatsApp(self, student_id: Any, direct_message_text: str) -> bool:
        """Launches WhatsApp with the exact customized message text for this student."""
        try:
            import urllib.parse
            import webbrowser
            import os

            student = StudentController.get_student_by_id(str(student_id))
            if not student or not student.mobile_no:
                self.messageDispatched.emit(False, "Student does not have a valid mobile number.")
                return False

            phone = MessageController.normalize_phone_number(student.mobile_no)
            encoded_msg = urllib.parse.quote(direct_message_text)

            # 1. Desktop protocol
            desktop_url = f"whatsapp://send?phone={phone}&text={encoded_msg}"
            # 2. Universal API web URL (redirects to WhatsApp App on desktop or web)
            web_url = f"https://api.whatsapp.com/send?phone={phone}&text={encoded_msg}"

            opened = False
            try:
                # Try opening desktop protocol first
                opened = QDesktopServices.openUrl(QUrl(desktop_url))
            except Exception:
                opened = False

            if not opened:
                try:
                    opened = webbrowser.open(web_url, new=2)
                except Exception:
                    try:
                        os.startfile(web_url)
                        opened = True
                    except Exception:
                        opened = QDesktopServices.openUrl(QUrl(web_url))

            if opened:
                self.messageDispatched.emit(True, f"WhatsApp dispatched for {student.name}.")
                return True
            else:
                webbrowser.open(web_url)
                self.messageDispatched.emit(True, f"WhatsApp opened for {student.name}.")
                return True

        except Exception as e:
            logger.error(f"Error sending direct WhatsApp: {e}")
            self.messageDispatched.emit(False, str(e))
            return False

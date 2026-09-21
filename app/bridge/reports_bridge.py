import os
import re
import shutil
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Signal, Slot, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QApplication, QFileDialog

from app.core.config import DATA_DIR, RECEIPTS_DIR, EXPORTS_DIR, BACKUPS_DIR
from app.modules.students.controllers import StudentController
from app.modules.students.reports import ReportGenerator

logger = logging.getLogger("CRM.ReportsBridge")


class ReportsBridge(QObject):
    """Bridge for Student PDF Generation, System Reports, and Document Management."""

    reportGenerated = Signal(bool, str, str)  # success, message, file_path
    documentsRefreshed = Signal()

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

    @Slot(result="QVariantList")
    def getStudentsList(self) -> List[Dict[str, Any]]:
        """Returns simplified student directory for PDF generation selector."""
        try:
            students = StudentController.get_all_students()
            res = []
            for s in students:
                bal = float(getattr(s, 'balance_due', 0.0) or 0.0)
                tot_paid = float(getattr(s, 'total_paid', 0.0) or 0.0)
                tot_fee = float(getattr(s, 'net_fee', 0.0) or getattr(s, 'total_fee', 0.0) or 0.0)
                
                last_paid = ""
                if getattr(s, "last_payment_date", None):
                    last_paid = s.last_payment_date.strftime("%d %b %Y")

                res.append({
                    "id": str(s.id),
                    "id_no": s.id_no or "",
                    "name": s.name or "",
                    "course_name": s.course_name or "",
                    "mobile_no": s.mobile_no or "",
                    "status": s.status or "Active",
                    "balance_due": bal,
                    "total_paid": tot_paid,
                    "total_fee": tot_fee,
                    "fee_status": s.fee_status or "Pending",
                    "admission_date_str": s.admission_date.strftime("%d %b %Y") if s.admission_date else "",
                    "last_paid_date_str": last_paid or "No payment yet",
                })
            return res
        except Exception as e:
            logger.error(f"Error getting students list: {e}")
            return []

    @Slot(str, str, result=str)
    @Slot(int, str, result=str)
    @Slot("QVariant", str, result=str)
    @Slot(str, result=str)
    @Slot(int, result=str)
    @Slot("QVariant", result=str)
    def generateStudentPdfWithSaveDialog(self, student_id: Any, doc_type: str = "admission") -> str:
        """Prompts native Windows Save File Dialog to let user save student PDF on PC."""
        try:
            student = StudentController.get_student_by_id(str(student_id))
            if not student:
                self.reportGenerated.emit(False, "Student not found.", "")
                return ""

            safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', student.name or "Student")
            type_label = "Admission_Slip" if doc_type == "admission" else ("Fee_Receipt" if doc_type == "fee_receipt" else "Profile_Summary")
            suggested_filename = f"{safe_name}_{type_label}_{datetime.now().strftime('%Y%m%d')}.pdf"

            parent_win = QApplication.activeWindow()
            file_path, _ = QFileDialog.getSaveFileName(
                parent_win,
                f"Save {student.name}'s PDF Document",
                suggested_filename,
                "PDF Document (*.pdf);;All Files (*.*)",
            )

            if not file_path:
                return ""

            if doc_type == "fee_receipt":
                out = ReportGenerator.generate_fee_receipt_pdf(student, output_path=file_path)
            elif doc_type == "profile":
                out = ReportGenerator.generate_student_profile_pdf(student, output_path=file_path)
            else:
                out = ReportGenerator.generate_admission_slip_pdf(student, output_path=file_path)

            self.reportGenerated.emit(True, f"PDF saved successfully to {Path(file_path).name}", file_path)
            self.documentsRefreshed.emit()

            try:
                os.startfile(file_path)
            except Exception:
                pass

            return file_path
        except Exception as e:
            logger.error(f"Error generating student PDF: {e}")
            self.reportGenerated.emit(False, str(e), "")
            return ""

    @Slot(str, str, result=str)
    @Slot(int, str, result=str)
    @Slot("QVariant", str, result=str)
    @Slot(str, result=str)
    @Slot(int, result=str)
    @Slot("QVariant", result=str)
    def previewStudentPdf(self, student_id: Any, doc_type: str = "admission") -> str:
        """Generates PDF and opens it immediately in system default PDF viewer."""
        try:
            student = StudentController.get_student_by_id(str(student_id))
            if not student:
                self.reportGenerated.emit(False, "Student not found.", "")
                return ""

            if doc_type == "fee_receipt":
                out = ReportGenerator.generate_fee_receipt_pdf(student)
            elif doc_type == "profile":
                out = ReportGenerator.generate_student_profile_pdf(student)
            else:
                out = ReportGenerator.generate_admission_slip_pdf(student)

            self.reportGenerated.emit(True, f"Opened {Path(out).name}", out)
            self.documentsRefreshed.emit()

            try:
                os.startfile(out)
            except Exception:
                QDesktopServices.openUrl(QUrl.fromLocalFile(out))

            return out
        except Exception as e:
            logger.error(f"Error previewing student PDF: {e}")
            self.reportGenerated.emit(False, str(e), "")
            return ""

    @Slot(result=str)
    @Slot(str, result=str)
    @Slot(str, str, result=str)
    @Slot(str, str, str, result=str)
    @Slot(str, str, str, str, result=str)
    def generateStudentRosterReport(
        self,
        search: str = "",
        status: str = "All",
        course: str = "All",
        fee: str = "All",
    ) -> str:
        """Generates comprehensive student roster Excel export to default directory."""
        try:
            students = StudentController.get_all_students(
                search_query=search if search.strip() else None,
                status_filter=status if status != "All" else None,
                course_filter=course if course != "All" else None,
                fee_filter=fee if fee != "All" else None,
            )
            excel_path = ReportGenerator.export_students_to_excel(students)
            self.reportGenerated.emit(True, f"Generated roster export with {len(students)} students.", excel_path)
            self.documentsRefreshed.emit()
            return excel_path
        except Exception as e:
            logger.error(f"Error generating roster report: {e}")
            self.reportGenerated.emit(False, str(e), "")
            return ""

    @Slot(result=str)
    @Slot(str, result=str)
    @Slot(str, str, result=str)
    @Slot(str, str, str, result=str)
    @Slot(str, str, str, str, result=str)
    def generateStudentRosterWithSaveDialog(
        self,
        search: str = "",
        status: str = "All",
        course: str = "All",
        fee: str = "All",
    ) -> str:
        """Prompts Windows Save File Dialog to export student roster Excel."""
        try:
            students = StudentController.get_all_students(
                search_query=search if search.strip() else None,
                status_filter=status if status != "All" else None,
                course_filter=course if course != "All" else None,
                fee_filter=fee if fee != "All" else None,
            )

            suggested_filename = f"Students_Master_Roster_{datetime.now().strftime('%Y%m%d')}.xlsx"
            parent_win = QApplication.activeWindow()
            file_path, _ = QFileDialog.getSaveFileName(
                parent_win,
                "Save Student Roster Excel Export",
                suggested_filename,
                "Excel Spreadsheet (*.xlsx);;All Files (*.*)",
            )

            if not file_path:
                return ""

            excel_path = ReportGenerator.export_students_to_excel(students, output_path=file_path)
            self.reportGenerated.emit(True, f"Roster saved to {Path(excel_path).name}", excel_path)
            self.documentsRefreshed.emit()

            try:
                os.startfile(excel_path)
            except Exception:
                pass

            return excel_path
        except Exception as e:
            logger.error(f"Error exporting roster with save dialog: {e}")
            self.reportGenerated.emit(False, str(e), "")
            return ""

    @Slot(result=str)
    def generateFeeLedgerWithSaveDialog(self) -> str:
        """Prompts Windows Save File Dialog to export fee collections & installments ledger."""
        try:
            students = StudentController.get_all_students()
            suggested_filename = f"Fee_Collections_Ledger_{datetime.now().strftime('%Y%m%d')}.xlsx"
            parent_win = QApplication.activeWindow()
            file_path, _ = QFileDialog.getSaveFileName(
                parent_win,
                "Save Fee Collections Ledger",
                suggested_filename,
                "Excel Spreadsheet (*.xlsx);;All Files (*.*)",
            )

            if not file_path:
                return ""

            excel_path = ReportGenerator.export_fee_ledger_to_excel(students, output_path=file_path)
            self.reportGenerated.emit(True, f"Fee ledger saved to {Path(excel_path).name}", excel_path)
            self.documentsRefreshed.emit()

            try:
                os.startfile(excel_path)
            except Exception:
                pass

            return excel_path
        except Exception as e:
            logger.error(f"Error exporting fee ledger: {e}")
            self.reportGenerated.emit(False, str(e), "")
            return ""

    @Slot(result=str)
    def generateOverdueReportWithSaveDialog(self) -> str:
        """Prompts Windows Save File Dialog to export overdue fee defaulters report."""
        try:
            students = StudentController.get_all_students()
            suggested_filename = f"Overdue_Dues_Report_{datetime.now().strftime('%Y%m%d')}.xlsx"
            parent_win = QApplication.activeWindow()
            file_path, _ = QFileDialog.getSaveFileName(
                parent_win,
                "Save Overdue Fee Recovery Report",
                suggested_filename,
                "Excel Spreadsheet (*.xlsx);;All Files (*.*)",
            )

            if not file_path:
                return ""

            excel_path = ReportGenerator.export_overdue_dues_to_excel(students, output_path=file_path)
            self.reportGenerated.emit(True, f"Overdue report saved to {Path(excel_path).name}", excel_path)
            self.documentsRefreshed.emit()

            try:
                os.startfile(excel_path)
            except Exception:
                pass

            return excel_path
        except Exception as e:
            logger.error(f"Error exporting overdue report: {e}")
            self.reportGenerated.emit(False, str(e), "")
            return ""

    @Slot(str, result=str)
    def saveDocumentAs(self, source_file_path: str) -> str:
        """Saves a copy of an existing document archive file to user-chosen PC location."""
        try:
            src = Path(source_file_path)
            if not src.exists():
                self.reportGenerated.emit(False, "Source file not found.", "")
                return ""

            parent_win = QApplication.activeWindow()
            file_ext = src.suffix.lower()
            filter_str = f"Document (*{file_ext});;All Files (*.*)" if file_ext else "All Files (*.*)"
            file_path, _ = QFileDialog.getSaveFileName(
                parent_win,
                "Save Document Copy As",
                src.name,
                filter_str,
            )

            if not file_path:
                return ""

            shutil.copy2(str(src), file_path)
            self.reportGenerated.emit(True, f"File saved to {Path(file_path).name}", file_path)
            return file_path
        except Exception as e:
            logger.error(f"Error copying document: {e}")
            self.reportGenerated.emit(False, str(e), "")
            return ""

    @Slot(result="QVariantList")
    def getDocumentList(self) -> List[Dict[str, Any]]:
        """Lists generated PDF receipts, Excel sheets, and backup files."""
        items = []
        try:
            # 1. Receipts (PDFs)
            if RECEIPTS_DIR.exists():
                for f in sorted(RECEIPTS_DIR.glob("*.pdf"), key=os.path.getmtime, reverse=True)[:50]:
                    items.append({
                        "name": f.name,
                        "category": "Receipts",
                        "type": "PDF Document",
                        "size_kb": f.stat().st_size // 1024,
                        "created_at": datetime.fromtimestamp(f.stat().st_mtime).strftime("%d %b %Y, %I:%M %p"),
                        "file_path": str(f.resolve()),
                    })

            # 2. Exports (Excel & CSV)
            if EXPORTS_DIR.exists():
                for f in sorted(EXPORTS_DIR.glob("*.*"), key=os.path.getmtime, reverse=True)[:50]:
                    items.append({
                        "name": f.name,
                        "category": "Exports",
                        "type": "Excel Spreadsheet" if f.suffix.lower() == ".xlsx" else "Document",
                        "size_kb": f.stat().st_size // 1024,
                        "created_at": datetime.fromtimestamp(f.stat().st_mtime).strftime("%d %b %Y, %I:%M %p"),
                        "file_path": str(f.resolve()),
                    })

            # 3. Backups
            if BACKUPS_DIR.exists():
                for f in sorted(BACKUPS_DIR.glob("*.db"), key=os.path.getmtime, reverse=True)[:20]:
                    items.append({
                        "name": f.name,
                        "category": "Backups",
                        "type": "Database Backup",
                        "size_kb": f.stat().st_size // 1024,
                        "created_at": datetime.fromtimestamp(f.stat().st_mtime).strftime("%d %b %Y, %I:%M %p"),
                        "file_path": str(f.resolve()),
                    })

        except Exception as e:
            logger.error(f"Error scanning document directory: {e}")

        return items

    @Slot(str)
    def openDocument(self, file_path: str):
        """Opens a document in the default desktop application."""
        try:
            p = Path(file_path)
            if p.exists():
                clean_path = str(p.resolve())
                try:
                    os.startfile(clean_path)
                except Exception:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(clean_path))
            else:
                logger.warning(f"Document not found: {file_path}")
        except Exception as e:
            logger.error(f"Error opening document: {e}")

    @Slot(str)
    def showInFolder(self, file_path: str):
        """Opens Explorer with the file selected."""
        try:
            p = Path(file_path)
            if p.exists():
                clean_path = str(p.resolve())
                try:
                    subprocess.Popen(f'explorer /select,"{clean_path}"')
                except Exception:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(str(p.parent.resolve())))
        except Exception as e:
            logger.error(f"Error opening folder: {e}")

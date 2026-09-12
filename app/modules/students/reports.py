import csv
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from app.core.config import RECEIPTS_DIR, EXPORTS_DIR, PHOTOS_DIR, ORGANIZATION_NAME
from app.models.student import Student

class ReportGenerator:
    """Generates printable PDFs, Admission Slips, and Data Exports."""

    @staticmethod
    def generate_admission_slip_pdf(student: Student) -> str:
        """Generates a high-quality admission & fee receipt PDF mirroring the physical CADDESK form."""
        filename = f"Admission_{student.id_no.replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = RECEIPTS_DIR / filename

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()
        
        # Custom Paragraph Styles
        header_title_style = ParagraphStyle(
            "OrgTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#A81D1D"),
            alignment=1, # Center
            fontName="Helvetica-Bold",
        )
        
        sub_title_style = ParagraphStyle(
            "SubTitle",
            parent=styles["Normal"],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#555555"),
            alignment=1,
            fontName="Helvetica",
        )

        label_style = ParagraphStyle(
            "FormLabel",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#222222"),
            fontName="Helvetica-Bold",
        )

        value_style = ParagraphStyle(
            "FormValue",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#111111"),
            fontName="Helvetica",
        )

        table_header_style = ParagraphStyle(
            "TableHeader",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            textColor=colors.white,
            alignment=1,
            fontName="Helvetica-Bold",
        )

        table_cell_style = ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#222222"),
            alignment=1,
            fontName="Helvetica",
        )

        elements = []

        # 1. Header Banner
        elements.append(Paragraph(ORGANIZATION_NAME, header_title_style))
        elements.append(Paragraph("SKILL INDIA & MSME AFFILIATED CENTRE • ADMISSION & REGISTRATION FORM", sub_title_style))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#A81D1D"), spaceAfter=12))

        # 2. Top Meta: ID No, Online Reg, and Student Photo
        id_text = f"<b>ID No:</b> {student.id_no or 'N/A'}"
        online_text = f"<b>Online Status:</b> {'Yes (' + (student.online_reg_no or '') + ')' if student.is_online else 'Offline'}"
        adm_date = f"<b>Admission Date:</b> {student.admission_date.strftime('%d/%m/%Y') if student.admission_date else 'N/A'}"
        
        meta_html = f"{id_text}<br/><br/>{online_text}<br/><br/>{adm_date}"

        # Check Photo
        photo_flowable = Paragraph("<b>[ Photo ]</b>", ParagraphStyle("NoPhoto", alignment=1, textColor=colors.gray))
        if student.photo_path:
            p_path = PHOTOS_DIR / student.photo_path
            if p_path.exists():
                try:
                    photo_flowable = Image(str(p_path), width=75, height=95)
                except Exception:
                    pass

        top_table_data = [
            [Paragraph(meta_html, value_style), photo_flowable]
        ]
        top_table = Table(top_table_data, colWidths=[420, 100])
        top_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOX", (1, 0), (1, 0), 1, colors.HexColor("#CCCCCC")),
            ("ALIGN", (1, 0), (1, 0), "CENTER"),
        ]))
        elements.append(top_table)
        elements.append(Spacer(1, 10))

        # 3. Personal & Contact Details Grid
        personal_data = [
            [Paragraph("Student Name:", label_style), Paragraph(student.name or "", value_style), Paragraph("Father's Name:", label_style), Paragraph(student.father_name or "", value_style)],
            [Paragraph("Mother's Name:", label_style), Paragraph(student.mother_name or "", value_style), Paragraph("Date of Birth:", label_style), Paragraph(student.dob.strftime('%d/%m/%Y') if student.dob else "N/A", value_style)],
            [Paragraph("Father's Occ.:", label_style), Paragraph(student.father_occupation or "", value_style), Paragraph("Aadhar No:", label_style), Paragraph(student.aadhar_no or "", value_style)],
            [Paragraph("College/School:", label_style), Paragraph(student.college_school or "", value_style), Paragraph("Year / Sem:", label_style), Paragraph(student.year_sem or "", value_style)],
            [Paragraph("Mobile No:", label_style), Paragraph(student.mobile_no or "", value_style), Paragraph("Email ID:", label_style), Paragraph(student.email or "", value_style)],
            [Paragraph("Father's Contact:", label_style), Paragraph(student.father_contact_no or "", value_style), Paragraph("Alt. Contact:", label_style), Paragraph(student.alternate_contact_no or "", value_style)],
            [Paragraph("Permanent Address:", label_style), Paragraph(f"{student.permanent_address or ''}", value_style), Paragraph("District/State/PIN:", label_style), Paragraph(f"{student.district or ''}, {student.state or ''} - {student.pin_code or ''}", value_style)],
            [Paragraph("Enrolled Course:", label_style), Paragraph(f"<b>{student.course_name or 'N/A'}</b>", value_style), Paragraph("Status:", label_style), Paragraph(f"<b>{student.status}</b>", value_style)],
        ]
        personal_table = Table(personal_data, colWidths=[110, 150, 110, 150])
        personal_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F8F8F8")),
            ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#F8F8F8")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(personal_table)
        elements.append(Spacer(1, 14))

        # 4. Fee Installment Schedule & Ledger
        elements.append(Paragraph("<b>Fee Schedule & Payment Ledger</b>", label_style))
        elements.append(Spacer(1, 4))

        fee_table_data = [[
            Paragraph("Inst.", table_header_style),
            Paragraph("Due (Rs.)", table_header_style),
            Paragraph("Paid (Rs.)", table_header_style),
            Paragraph("Pay Date", table_header_style),
            Paragraph("Mode", table_header_style),
            Paragraph("Receipt / Ref", table_header_style),
            Paragraph("Status", table_header_style),
        ]]

        installments = student.fee_installments or []
        running_due = float(student.net_fee or 0.0)
        for idx, inst in enumerate(installments):
            paid_amt = float(inst.paid_amount or 0.0)
            if paid_amt > 0 or idx == 0:
                cur_due = running_due
            elif running_due > 0 and idx > 0 and (float(installments[idx - 1].paid_amount or 0.0) > 0):
                cur_due = running_due
            elif inst.due_amount and inst.due_amount > 0:
                cur_due = float(inst.due_amount)
            else:
                cur_due = 0.0

            if paid_amt > 0 or cur_due > 0:
                fee_table_data.append([
                    Paragraph(inst.installment_label, table_cell_style),
                    Paragraph(f"{cur_due:,.2f}", table_cell_style),
                    Paragraph(f"{paid_amt:,.2f}", table_cell_style),
                    Paragraph(inst.payment_date.strftime('%d/%m/%Y') if inst.payment_date else "-", table_cell_style),
                    Paragraph(inst.payment_mode or "-", table_cell_style),
                    Paragraph(inst.transaction_ref or "-", table_cell_style),
                    Paragraph("Paid" if paid_amt > 0 else "Pending", table_cell_style),
                ])
            running_due = max(0.0, running_due - paid_amt)

        if len(fee_table_data) == 1:
            fee_table_data.append([Paragraph("1st", table_cell_style), Paragraph(f"{student.net_fee:,.2f}", table_cell_style), Paragraph(f"{student.total_paid:,.2f}", table_cell_style), Paragraph("-", table_cell_style), Paragraph("-", table_cell_style), Paragraph("-", table_cell_style), Paragraph(student.fee_status, table_cell_style)])

        # Totals Summary Row
        fee_table_data.append([
            Paragraph("<b>TOTALS</b>", table_cell_style),
            Paragraph(f"<b>Rs. {student.net_fee:,.2f}</b>", table_cell_style),
            Paragraph(f"<b>Rs. {student.total_paid:,.2f}</b>", table_cell_style),
            Paragraph(f"<b>Bal: Rs. {student.balance_due:,.2f}</b>", table_cell_style),
            Paragraph("-", table_cell_style),
            Paragraph("-", table_cell_style),
            Paragraph(f"<b>{student.fee_status}</b>", table_cell_style),
        ])

        fee_table = Table(fee_table_data, colWidths=[40, 75, 75, 80, 80, 100, 70])
        fee_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#EEEEEE")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 3),
        ]))
        elements.append(fee_table)
        elements.append(Spacer(1, 10))

        # 6. Declaration & Signatures
        declaration_text = (
            "<b>Declaration:</b> I hereby declare that all information provided above is true and correct. "
            "I have read and understood the rules, installment schedules, and refund policies of CADDESK CENTRE. "
            "Course fees once paid cannot be refunded after commencement."
        )
        elements.append(Paragraph(declaration_text, ParagraphStyle("Decl", parent=styles["Normal"], fontSize=7, leading=9, textColor=colors.HexColor("#555555"))))
        elements.append(Spacer(1, 20))

        sig_data = [
            [Paragraph("______________________<br/><b>Student Signature</b>", ParagraphStyle("Sig1", alignment=0, fontSize=8, leading=11)),
             Paragraph("______________________<br/><b>Authorized Centre Stamp / Sign</b>", ParagraphStyle("Sig2", alignment=2, fontSize=8, leading=11))]
        ]
        sig_table = Table(sig_data, colWidths=[260, 260])
        sig_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
        elements.append(sig_table)

        doc.build(elements)
        return str(output_path)

    @staticmethod
    def export_students_to_excel(students: List[Student]) -> str:
        """Exports student list and fee metrics to an Excel (.xlsx) file."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Students Directory"

        # Headers
        headers = [
            "ID No", "Student Name", "Father Name", "Mobile No", "Email",
            "Course", "Year/Sem", "Aadhar No", "College/School",
            "District", "State", "PIN", "Status", "Admission Date",
            "Total Fee (Rs.)", "Discount (Rs.)", "Net Fee (Rs.)",
            "Total Paid (Rs.)", "Balance Due (Rs.)", "Fee Status"
        ]
        ws.append(headers)

        # Style Header Row
        header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # Append student rows
        for s in students:
            row = [
                s.id_no,
                s.name,
                s.father_name or "",
                s.mobile_no,
                s.email or "",
                s.course_name or "",
                s.year_sem or "",
                s.aadhar_no or "",
                s.college_school or "",
                s.district or "",
                s.state or "",
                s.pin_code or "",
                s.status,
                s.admission_date.strftime("%d-%m-%Y") if s.admission_date else "",
                s.total_fee,
                s.discount_amount,
                s.net_fee,
                s.total_paid,
                s.balance_due,
                s.fee_status,
            ]
            ws.append(row)

        # Auto-adjust column widths
        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

        filename = f"Students_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        export_path = EXPORTS_DIR / filename
        wb.save(str(export_path))
        return str(export_path)

    @staticmethod
    def export_students_to_csv(students: List[Student]) -> str:
        """Exports student list to a portable CSV file."""
        filename = f"Students_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        export_path = EXPORTS_DIR / filename

        with open(export_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([
                "ID No", "Student Name", "Father Name", "Mobile No", "Email",
                "Course", "Year/Sem", "Aadhar No", "College/School",
                "District", "State", "PIN", "Status", "Admission Date",
                "Total Fee", "Discount", "Net Fee", "Total Paid", "Balance Due", "Fee Status"
            ])
            for s in students:
                writer.writerow([
                    s.id_no,
                    s.name,
                    s.father_name or "",
                    s.mobile_no,
                    s.email or "",
                    s.course_name or "",
                    s.year_sem or "",
                    s.aadhar_no or "",
                    s.college_school or "",
                    s.district or "",
                    s.state or "",
                    s.pin_code or "",
                    s.status,
                    s.admission_date.strftime("%Y-%m-%d") if s.admission_date else "",
                    s.total_fee,
                    s.discount_amount,
                    s.net_fee,
                    s.total_paid,
                    s.balance_due,
                    s.fee_status,
                ])

        return str(export_path)

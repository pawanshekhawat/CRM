import csv
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from app.core.config import RECEIPTS_DIR, EXPORTS_DIR, PHOTOS_DIR, ORGANIZATION_NAME
from app.models.student import Student


class ReportGenerator:
    """Generates printable PDFs, Admission Slips, Fee Receipts, and Data Exports."""

    @staticmethod
    def generate_admission_slip_pdf(student: Student, output_path: Optional[str] = None) -> str:
        """Generates a high-quality admission & registration PDF mirroring the physical CADDESK form."""
        if not output_path:
            id_str = (student.id_no or "STU").replace("/", "_")
            filename = f"Admission_{id_str}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            target = RECEIPTS_DIR / filename
        else:
            target = Path(output_path)
            target.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            str(target),
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        header_title_style = ParagraphStyle(
            "OrgTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#A81D1D"),
            alignment=1,
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
        elements.append(Paragraph("SKILL INDIA & MSME AFFILIATED CENTRE • OFFICIAL ADMISSION & REGISTRATION SLIP", sub_title_style))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#A81D1D"), spaceAfter=12))

        # 2. Top Meta & Student Photo
        id_text = f"<b>Student ID:</b> {student.id_no or 'N/A'}"
        online_text = f"<b>Online Reg:</b> {'Yes (' + (student.online_reg_no or '') + ')' if student.is_online else 'Offline'}"
        adm_date = f"<b>Admission Date:</b> {student.admission_date.strftime('%d/%m/%Y') if student.admission_date else 'N/A'}"

        meta_html = f"{id_text}<br/><br/>{online_text}<br/><br/>{adm_date}"

        photo_flowable = Paragraph("<b>[ Photo ]</b>", ParagraphStyle("NoPhoto", alignment=1, textColor=colors.gray))
        if student.photo_path:
            p_path = PHOTOS_DIR / student.photo_path
            if p_path.exists():
                try:
                    photo_flowable = Image(str(p_path), width=75, height=95)
                except Exception:
                    pass

        top_table_data = [[Paragraph(meta_html, value_style), photo_flowable]]
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
            [Paragraph("Referred By:", label_style), Paragraph(f"{student.referred_by.name} ({student.referred_by.id_no})" if student.referred_by else "Direct / None", value_style), Paragraph("Referral Disc:", label_style), Paragraph(f"Rs. {student.referral_discount:,.2f}" if student.referral_discount else "Rs. 0.00", value_style)],
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
                    Paragraph(inst.installment_label or f"{idx+1}st", table_cell_style),
                    Paragraph(f"{cur_due:,.2f}", table_cell_style),
                    Paragraph(f"{paid_amt:,.2f}", table_cell_style),
                    Paragraph(inst.payment_date.strftime('%d/%m/%Y') if inst.payment_date else "-", table_cell_style),
                    Paragraph(inst.payment_mode or "-", table_cell_style),
                    Paragraph(inst.transaction_ref or "-", table_cell_style),
                    Paragraph("Paid" if paid_amt > 0 else "Pending", table_cell_style),
                ])
            running_due = max(0.0, running_due - paid_amt)

        if len(fee_table_data) == 1:
            fee_table_data.append([
                Paragraph("1st", table_cell_style),
                Paragraph(f"{student.net_fee:,.2f}", table_cell_style),
                Paragraph(f"{student.total_paid:,.2f}", table_cell_style),
                Paragraph("-", table_cell_style),
                Paragraph("-", table_cell_style),
                Paragraph("-", table_cell_style),
                Paragraph(student.fee_status, table_cell_style)
            ])

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

        # 5. Declaration & Signatures
        declaration_text = (
            "<b>Declaration:</b> I hereby declare that all information provided above is true and correct. "
            "I have read and understood the rules, installment schedules, and refund policies of CADDESK CENTRE. "
            "Course fees once paid cannot be refunded after commencement."
        )
        elements.append(Paragraph(declaration_text, ParagraphStyle("Decl", parent=styles["Normal"], fontSize=7, leading=9, textColor=colors.HexColor("#555555"))))
        elements.append(Spacer(1, 20))

        sig_data = [
            [
                Paragraph("______________________<br/><b>Student Signature</b>", ParagraphStyle("Sig1", alignment=0, fontSize=8, leading=11)),
                Paragraph("______________________<br/><b>Authorized Centre Stamp / Sign</b>", ParagraphStyle("Sig2", alignment=2, fontSize=8, leading=11))
            ]
        ]
        sig_table = Table(sig_data, colWidths=[260, 260])
        sig_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
        elements.append(sig_table)

        doc.build(elements)
        return str(target)

    @staticmethod
    def generate_fee_receipt_pdf(student: Student, output_path: Optional[str] = None) -> str:
        """Generates an official Fee Payment Receipt & Statement PDF."""
        if not output_path:
            id_str = (student.id_no or "STU").replace("/", "_")
            filename = f"Fee_Receipt_{id_str}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            target = RECEIPTS_DIR / filename
        else:
            target = Path(output_path)
            target.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            str(target),
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        header_title_style = ParagraphStyle(
            "ReceiptTitle",
            parent=styles["Heading1"],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#0D9488"),
            alignment=1,
            fontName="Helvetica-Bold",
        )

        sub_title_style = ParagraphStyle(
            "SubTitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#475569"),
            alignment=1,
            fontName="Helvetica",
        )

        label_style = ParagraphStyle(
            "FormLabel",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#1E293B"),
            fontName="Helvetica-Bold",
        )

        value_style = ParagraphStyle(
            "FormValue",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#0F172A"),
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
            textColor=colors.HexColor("#1E293B"),
            alignment=1,
            fontName="Helvetica",
        )

        elements = []

        # Header
        elements.append(Paragraph(ORGANIZATION_NAME, header_title_style))
        elements.append(Paragraph("OFFICIAL FEE PAYMENT RECEIPT & ACCOUNT STATEMENT", sub_title_style))
        elements.append(Spacer(1, 8))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0D9488"), spaceAfter=12))

        # Receipt Meta Info
        receipt_no = f"CD-REC-{datetime.now().strftime('%Y%m%d')}-{student.id or 1}"
        gen_date = datetime.now().strftime("%d %b %Y, %I:%M %p")
        meta_grid = [
            [Paragraph(f"<b>Receipt No:</b> {receipt_no}", value_style), Paragraph(f"<b>Date:</b> {gen_date}", value_style)],
            [Paragraph(f"<b>Student Name:</b> <b>{student.name}</b>", value_style), Paragraph(f"<b>Mobile:</b> {student.mobile_no}", value_style)],
            [Paragraph(f"<b>Course:</b> {student.course_name}", value_style), Paragraph(f"<b>Payment Status:</b> <b>{student.fee_status.upper()}</b>", value_style)],
        ]
        meta_table = Table(meta_grid, colWidths=[260, 260])
        meta_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 14))

        # Financial Summary Cards
        summary_grid = [
            [
                Paragraph("<b>Total Course Fee</b><br/><font size=12 color='#0F172A'><b>₹" + f"{student.total_fee:,.2f}" + "</b></font>", ParagraphStyle("C1", alignment=1)),
                Paragraph("<b>Discount Applied</b><br/><font size=12 color='#059669'><b>₹" + f"{student.discount_amount:,.2f}" + "</b></font>", ParagraphStyle("C2", alignment=1)),
                Paragraph("<b>Total Paid Amount</b><br/><font size=12 color='#0D9488'><b>₹" + f"{student.total_paid:,.2f}" + "</b></font>", ParagraphStyle("C3", alignment=1)),
                Paragraph("<b>Balance Due</b><br/><font size=12 color='#E11D48'><b>₹" + f"{student.balance_due:,.2f}" + "</b></font>", ParagraphStyle("C4", alignment=1)),
            ]
        ]
        summary_table = Table(summary_grid, colWidths=[130, 130, 130, 130])
        summary_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 14))

        # Installments Detail Table
        elements.append(Paragraph("<b>Recorded Installments & Payment Breakdown</b>", label_style))
        elements.append(Spacer(1, 4))

        inst_data = [[
            Paragraph("Installment", table_header_style),
            Paragraph("Due (₹)", table_header_style),
            Paragraph("Paid (₹)", table_header_style),
            Paragraph("Payment Date", table_header_style),
            Paragraph("Mode", table_header_style),
            Paragraph("Receipt / Ref", table_header_style),
            Paragraph("Status", table_header_style),
        ]]

        installments = student.fee_installments or []
        for idx, inst in enumerate(installments):
            paid_val = float(inst.paid_amount or 0.0)
            due_val = float(inst.due_amount or 0.0)
            if paid_val > 0 or due_val > 0:
                inst_data.append([
                    Paragraph(inst.installment_label or f"Installment #{idx+1}", table_cell_style),
                    Paragraph(f"₹{due_val:,.2f}", table_cell_style),
                    Paragraph(f"₹{paid_val:,.2f}", table_cell_style),
                    Paragraph(inst.payment_date.strftime('%d %b %Y') if inst.payment_date else "—", table_cell_style),
                    Paragraph(inst.payment_mode or "Cash", table_cell_style),
                    Paragraph(inst.transaction_ref or "—", table_cell_style),
                    Paragraph("<font color='#059669'><b>PAID</b></font>" if paid_val > 0 else "<font color='#DC2626'>Pending</font>", table_cell_style),
                ])

        if len(inst_data) == 1:
            inst_data.append([
                Paragraph("1st Installment", table_cell_style),
                Paragraph(f"₹{student.net_fee:,.2f}", table_cell_style),
                Paragraph(f"₹{student.total_paid:,.2f}", table_cell_style),
                Paragraph(student.last_payment_date.strftime('%d %b %Y') if student.last_payment_date else "—", table_cell_style),
                Paragraph("Cash / UPI", table_cell_style),
                Paragraph("—", table_cell_style),
                Paragraph(f"<b>{student.fee_status}</b>", table_cell_style)
            ])

        inst_table = Table(inst_data, colWidths=[90, 75, 75, 80, 70, 80, 50])
        inst_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F766E")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(inst_table)
        elements.append(Spacer(1, 20))

        # Signatures
        sig_data = [
            [
                Paragraph("<i>This is a computer-generated official receipt.</i>", ParagraphStyle("Note", fontSize=8, textColor=colors.gray)),
                Paragraph("__________________________<br/><b>Accounts Officer / Cashier</b>", ParagraphStyle("Sig", alignment=2, fontSize=8, leading=11))
            ]
        ]
        sig_table = Table(sig_data, colWidths=[260, 260])
        sig_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
        elements.append(sig_table)

        doc.build(elements)
        return str(target)

    @staticmethod
    def generate_student_profile_pdf(student: Student, output_path: Optional[str] = None) -> str:
        """Generates a complete Student Profile & Academic Dossier PDF."""
        return ReportGenerator.generate_admission_slip_pdf(student, output_path=output_path)

    @staticmethod
    def export_students_to_excel(students: List[Student], output_path: Optional[str] = None) -> str:
        """Exports student list and fee metrics to an Excel (.xlsx) file."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Students Directory"

        headers = [
            "ID No", "Student Name", "Father Name", "Mobile No", "Email",
            "Course", "Year/Sem", "Aadhar No", "College/School",
            "District", "State", "PIN", "Status", "Admission Date",
            "Total Fee (Rs.)", "Discount (Rs.)", "Net Fee (Rs.)",
            "Total Paid (Rs.)", "Balance Due (Rs.)", "Fee Status",
            "Last Paid Date", "Days Since Last Paid", "Last Paid Amount (Rs.)",
            "Referred By", "Referral Disc (Rs.)", "Referral Comm (Rs.)",
            "Referrals Count", "Total Comm Earned (Rs.)"
        ]
        ws.append(headers)

        header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")

        for s in students:
            ref_by_text = f"{s.referred_by.name} ({s.referred_by.id_no})" if s.referred_by else "Direct / None"
            last_dt_str = s.last_payment_date.strftime("%d-%m-%Y") if s.last_payment_date else "No Payment"
            days_ago_val = s.days_since_last_payment if s.days_since_last_payment is not None else ""
            last_amt = s.latest_paid_installment.paid_amount if (s.latest_paid_installment and s.latest_paid_installment.paid_amount) else 0.0
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
                last_dt_str,
                days_ago_val,
                last_amt,
                ref_by_text,
                s.referral_discount or 0.0,
                s.referral_commission or 0.0,
                s.referrals_count,
                s.total_referral_commission_earned,
            ]
            ws.append(row)

        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

        if not output_path:
            filename = f"Students_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            export_path = EXPORTS_DIR / filename
        else:
            export_path = Path(output_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)

        wb.save(str(export_path))
        return str(export_path)

    @staticmethod
    def export_fee_ledger_to_excel(students: List[Student], output_path: Optional[str] = None) -> str:
        """Exports fee collections and installment transactions to an Excel (.xlsx) file."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Fee Collections Ledger"

        headers = [
            "Receipt Ref", "Student ID", "Student Name", "Mobile No", "Course",
            "Installment", "Due Amount (Rs.)", "Paid Amount (Rs.)", "Payment Date",
            "Payment Mode", "Balance Due (Rs.)", "Fee Status"
        ]
        ws.append(headers)

        header_fill = PatternFill(start_color="0D9488", end_color="0D9488", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")

        for s in students:
            for inst in (s.fee_installments or []):
                paid_amt = float(inst.paid_amount or 0.0)
                if paid_amt > 0:
                    ws.append([
                        inst.transaction_ref or f"REC-{s.id}-{inst.id or 1}",
                        s.id_no or "",
                        s.name,
                        s.mobile_no,
                        s.course_name or "",
                        inst.installment_label or "Installment",
                        float(inst.due_amount or 0.0),
                        paid_amt,
                        inst.payment_date.strftime("%d-%m-%Y") if inst.payment_date else "",
                        inst.payment_mode or "Cash",
                        float(s.balance_due or 0.0),
                        s.fee_status,
                    ])

        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

        if not output_path:
            filename = f"Fee_Collections_Ledger_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            export_path = EXPORTS_DIR / filename
        else:
            export_path = Path(output_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)

        wb.save(str(export_path))
        return str(export_path)

    @staticmethod
    def export_overdue_dues_to_excel(students: List[Student], output_path: Optional[str] = None) -> str:
        """Exports list of defaulters and pending fee balances to an Excel (.xlsx) file."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Overdue Dues Report"

        headers = [
            "Student Name", "Mobile No", "Course", "Total Fee (Rs.)", "Total Paid (Rs.)",
            "Outstanding Balance (Rs.)", "Last Payment Date", "Days Since Last Payment",
            "Father Name", "Father Contact", "Fee Status"
        ]
        ws.append(headers)

        header_fill = PatternFill(start_color="BE123C", end_color="BE123C", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")

        defaulters = [s for s in students if float(getattr(s, 'balance_due', 0.0) or 0.0) > 0]
        for s in defaulters:
            last_dt_str = s.last_payment_date.strftime("%d-%m-%Y") if s.last_payment_date else "No Payment Recorded"
            days_ago_val = s.days_since_last_payment if s.days_since_last_payment is not None else "—"
            ws.append([
                s.name,
                s.mobile_no,
                s.course_name or "",
                float(s.net_fee or 0.0),
                float(s.total_paid or 0.0),
                float(s.balance_due or 0.0),
                last_dt_str,
                days_ago_val,
                s.father_name or "",
                s.father_contact_no or "",
                s.fee_status,
            ])

        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

        if not output_path:
            filename = f"Overdue_Dues_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            export_path = EXPORTS_DIR / filename
        else:
            export_path = Path(output_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)

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
                "Total Fee", "Discount", "Net Fee", "Total Paid", "Balance Due", "Fee Status",
                "Last Paid Date", "Days Since Last Paid", "Last Paid Amount"
            ])
            for s in students:
                last_dt_str = s.last_payment_date.strftime("%Y-%m-%d") if s.last_payment_date else ""
                days_ago_val = s.days_since_last_payment if s.days_since_last_payment is not None else ""
                last_amt = s.latest_paid_installment.paid_amount if (s.latest_paid_installment and s.latest_paid_installment.paid_amount) else 0.0
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
                    last_dt_str,
                    days_ago_val,
                    last_amt,
                ])

        return str(export_path)

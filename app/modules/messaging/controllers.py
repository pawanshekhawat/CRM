import logging
import random
import re
import urllib.parse
from typing import Any, Dict, List, Optional

from app.core.database import get_db_session
from app.models.message_template import MessageTemplate
from app.models.student import Student

logger = logging.getLogger("CRM.MessagingController")

DEFAULT_TEMPLATES = [
    {
        "title": "Fee Reminder (Outstanding Balance)",
        "category": "Fees",
        "is_default": True,
        "sort_order": 1,
        "content": (
            "{Dear|Hello|Respected} {name}, this is a gentle reminder from CADDESK Centre regarding your {course} course. "
            "Your outstanding fee balance is ₹{balance_due}. Your last payment was made on {last_paid_date} ({days_ago} days ago). "
            "Kindly settle the pending installment at the accounts desk. Thank you!"
        ),
    },
    {
        "title": "Urgent Fee Overdue Notice",
        "category": "Fees",
        "is_default": True,
        "sort_order": 2,
        "content": (
            "{Urgent Fee Notice|Important Fee Update}: {Dear|Respected} {name}, your course fee balance of ₹{balance_due} for {course} "
            "is overdue by {days_ago} days since your last installment. Please contact the centre office or visit the accounts desk today."
        ),
    },
    {
        "title": "Admission Welcome & Confirmation",
        "category": "Admissions",
        "is_default": True,
        "sort_order": 3,
        "content": (
            "{Welcome to CADDESK|Warm Greetings from CADDESK Centre} {name}! We are pleased to confirm your admission for {course} "
            "(Student ID: {id_no}). Your classes and batch details will be shared shortly. Feel free to contact us for any assistance."
        ),
    },
    {
        "title": "Batch Timing & Schedule Notice",
        "category": "Batches",
        "is_default": True,
        "sort_order": 4,
        "content": (
            "{Dear|Hello} {name}, this is to inform you regarding your upcoming classes for {course}. "
            "Please ensure punctual attendance and bring your course notebooks. For schedule changes, reach out to your faculty."
        ),
    },
    {
        "title": "Certificate & Course Completion",
        "category": "General",
        "is_default": True,
        "sort_order": 5,
        "content": (
            "Congratulations {name}! You have successfully completed your training in {course} at CADDESK Centre. "
            "Your authorized certificate is ready for collection at the front desk. We wish you great success in your career!"
        ),
    },
]

SPINTAX_PATTERN = re.compile(r"\{([^{}]+?\|[^{}]+?)\}")


class MessageController:
    """Controller for WhatsApp message templates, variable interpolation, Spintax, and dispatch URLs."""

    @staticmethod
    def get_all_templates() -> List[MessageTemplate]:
        """Fetch all message templates ordered by sort_order and title."""
        with get_db_session() as session:
            templates = session.query(MessageTemplate).order_by(MessageTemplate.sort_order.asc(), MessageTemplate.title.asc()).all()
            if not templates:
                # Seed defaults if table is empty
                MessageController.seed_default_templates()
                templates = session.query(MessageTemplate).order_by(MessageTemplate.sort_order.asc(), MessageTemplate.title.asc()).all()
            session.expunge_all()
            return templates

    @staticmethod
    def get_template_by_id(template_id: str) -> Optional[MessageTemplate]:
        with get_db_session() as session:
            tmpl = session.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()
            if tmpl:
                session.expunge(tmpl)
            return tmpl

    @staticmethod
    def create_template(data: Dict[str, Any]) -> MessageTemplate:
        """Create a new message template."""
        with get_db_session() as session:
            tmpl = MessageTemplate(
                title=data.get("title", "Untitled Template").strip(),
                category=data.get("category", "General").strip(),
                content=data.get("content", "").strip(),
                is_default=bool(data.get("is_default", False)),
                sort_order=int(data.get("sort_order", 0)),
            )
            session.add(tmpl)
            session.commit()
            session.refresh(tmpl)
            session.expunge(tmpl)
            logger.info(f"Created message template: '{tmpl.title}'")
            return tmpl

    @staticmethod
    def update_template(template_id: str, data: Dict[str, Any]) -> Optional[MessageTemplate]:
        """Update an existing template."""
        with get_db_session() as session:
            tmpl = session.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()
            if not tmpl:
                return None
            if "title" in data:
                tmpl.title = data["title"].strip()
            if "category" in data:
                tmpl.category = data["category"].strip()
            if "content" in data:
                tmpl.content = data["content"].strip()
            if "sort_order" in data:
                tmpl.sort_order = int(data["sort_order"])
            session.commit()
            session.refresh(tmpl)
            session.expunge(tmpl)
            return tmpl

    @staticmethod
    def delete_template(template_id: str) -> bool:
        """Delete a template by ID."""
        with get_db_session() as session:
            tmpl = session.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()
            if not tmpl:
                return False
            session.delete(tmpl)
            session.commit()
            logger.info(f"Deleted message template ID: {template_id}")
            return True

    @staticmethod
    def seed_default_templates():
        """Populate initial standard CADDESK templates if empty."""
        with get_db_session() as session:
            existing_count = session.query(MessageTemplate).count()
            if existing_count > 0:
                return
            for item in DEFAULT_TEMPLATES:
                tmpl = MessageTemplate(
                    title=item["title"],
                    category=item["category"],
                    content=item["content"],
                    is_default=item["is_default"],
                    sort_order=item["sort_order"],
                )
                session.add(tmpl)
            session.commit()
            logger.info("Seeded default WhatsApp message templates.")

    @staticmethod
    def resolve_spintax(text: str) -> str:
        """
        Recursively resolves Spintax patterns like {Hello|Dear|Respected}
        by picking a random choice for each group.
        """
        while True:
            match = SPINTAX_PATTERN.search(text)
            if not match:
                break
            options = match.group(1).split("|")
            chosen = random.choice(options)
            text = text[:match.start()] + chosen + text[match.end():]
        return text

    @staticmethod
    def render_message(template_str: str, student: Student, randomize_spintax: bool = True) -> str:
        """
        Substitutes all student merge tags and resolves Spintax variations.
        """
        if not template_str or not student:
            return template_str or ""

        # 1. Resolve Spintax first if requested
        text = MessageController.resolve_spintax(template_str) if randomize_spintax else template_str

        # 2. Prepare dynamic values
        first_name = (student.name or "").strip().split()[0] if student.name else "Student"
        last_dt = student.last_payment_date
        last_dt_str = last_dt.strftime("%d %b %Y") if last_dt else "No prior payment"
        days_ago_val = str(student.days_since_last_payment) if student.days_since_last_payment is not None else "N/A"
        adm_dt_str = student.admission_date.strftime("%d %b %Y") if student.admission_date else "N/A"

        # 3. Dynamic Tag Map
        replacements = {
            "{name}": student.name or "Student",
            "{first_name}": first_name,
            "{id_no}": student.id_no or "",
            "{course}": student.course_name or "Course",
            "{balance_due}": f"{student.balance_due:,.0f}",
            "{total_paid}": f"{student.total_paid:,.0f}",
            "{net_fee}": f"{student.effective_net_fee:,.0f}",
            "{total_fee}": f"{student.total_fee:,.0f}",
            "{last_paid_date}": last_dt_str,
            "{days_ago}": days_ago_val,
            "{days_since_paid}": days_ago_val,
            "{admission_date}": adm_dt_str,
            "{father_name}": student.father_name or "",
            "{mobile_no}": student.mobile_no or "",
            "{college}": student.college_school or "",
            "{status}": student.status or "Active",
            "{fee_status}": student.fee_status or "Pending",
        }

        # Case-insensitive placeholder replacement
        for tag, val in replacements.items():
            pattern = re.compile(re.escape(tag), re.IGNORECASE)
            text = pattern.sub(val, text)

        return text.strip()

    @staticmethod
    def normalize_phone_number(mobile_no: str) -> str:
        """Cleans digits and prepends Indian country code 91 if 10-digit number."""
        clean = "".join(c for c in (mobile_no or "") if c.isdigit())
        if len(clean) == 10:
            return "91" + clean
        return clean

    @staticmethod
    def build_whatsapp_url(mobile_no: str, message_text: str, use_desktop_app: bool = True) -> str:
        """
        Builds a WhatsApp dispatch URL:
        - Desktop App: whatsapp://send?phone=919876543210&text=EncodedMessage
        - Web Browser: https://web.whatsapp.com/send?phone=919876543210&text=EncodedMessage
        """
        phone = MessageController.normalize_phone_number(mobile_no)
        encoded_msg = urllib.parse.quote(message_text)

        if use_desktop_app:
            return f"whatsapp://send?phone={phone}&text={encoded_msg}"
        return f"https://web.whatsapp.com/send?phone={phone}&text={encoded_msg}"

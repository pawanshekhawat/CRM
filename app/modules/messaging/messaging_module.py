from typing import Optional
from PySide6.QtWidgets import QWidget

from app.modules.base_module import BaseModule
from app.modules.messaging.views.messaging_view import MessagingView


class MessagingModule(BaseModule):
    """WhatsApp Message Automation & Workflows Module."""

    @property
    def module_id(self) -> str:
        return "messaging"

    @property
    def module_name(self) -> str:
        return "Message Automation"

    @property
    def module_icon(self) -> str:
        return "📢"

    @property
    def sort_order(self) -> int:
        return 4

    def create_widget(self, parent: Optional[QWidget] = None) -> QWidget:
        return MessagingView(parent=parent)

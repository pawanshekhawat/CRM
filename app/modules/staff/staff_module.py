from typing import Optional
from PySide6.QtWidgets import QWidget

from app.modules.base_module import BaseModule
from app.modules.staff.views.staff_list_view import StaffListView

class StaffModule(BaseModule):
    """Staff & Batch Management Module."""

    @property
    def module_id(self) -> str:
        return "staff"

    @property
    def module_name(self) -> str:
        return "Staff & Batches"

    @property
    def module_icon(self) -> str:
        return "👨‍🏫"

    @property
    def sort_order(self) -> int:
        return 2

    def create_widget(self, parent: Optional[QWidget] = None) -> QWidget:
        return StaffListView(parent=parent)

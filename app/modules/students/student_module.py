from typing import Optional
from PySide6.QtWidgets import QWidget

from app.modules.base_module import BaseModule
from app.modules.students.views.student_list_view import StudentListView

class StudentModule(BaseModule):
    """Core Students & Admissions Module."""

    @property
    def module_id(self) -> str:
        return "students"

    @property
    def module_name(self) -> str:
        return "Students & Admissions"

    @property
    def module_icon(self) -> str:
        return "🎓"

    @property
    def sort_order(self) -> int:
        return 1

    def create_widget(self, parent: Optional[QWidget] = None) -> QWidget:
        return StudentListView(parent=parent)

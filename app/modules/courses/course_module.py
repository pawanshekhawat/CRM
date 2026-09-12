from typing import Optional
from PySide6.QtWidgets import QWidget

from app.modules.base_module import BaseModule
from app.modules.courses.views.course_list_view import CourseListView

class CourseModule(BaseModule):
    """Courses & Fee Catalog Management Module."""

    @property
    def module_id(self) -> str:
        return "courses"

    @property
    def module_name(self) -> str:
        return "Courses & Fees"

    @property
    def module_icon(self) -> str:
        return "🎓"

    @property
    def sort_order(self) -> int:
        return 3

    def create_widget(self, parent: Optional[QWidget] = None) -> QWidget:
        return CourseListView(parent=parent)

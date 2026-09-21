import json
import logging
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Signal, Slot

from app.modules.courses.controllers import CourseController, DEFAULT_COURSES_CATALOG

logger = logging.getLogger("CRM.CoursesBridge")


def serialize_course(course: Any) -> Dict[str, Any]:
    """Serializes a Course model into a clean dictionary suitable for QML models."""
    if not course:
        return {}

    stats = CourseController.get_course_stats(course.name) if course.name else {"student_count": 0, "batch_count": 0}

    return {
        "id": str(course.id),
        "course_code": course.course_code or "",
        "name": course.name or "",
        "category": course.category or "General",
        "standard_fee": float(course.standard_fee or 0.0),
        "description": course.description or "",
        "status": course.status or "Active",
        "student_count": stats.get("student_count", 0),
        "batch_count": stats.get("batch_count", 0),
    }


class CoursesBridge(QObject):
    """Bridge for Course Catalog CRUD, Categories, and Analytics."""

    coursesChanged = Signal()
    courseSaved = Signal(bool, str, str)  # success, message, course_id

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

    @Slot(result="QVariantList")
    @Slot(str, result="QVariantList")
    @Slot(str, str, result="QVariantList")
    @Slot(str, str, str, result="QVariantList")
    def getCourses(
        self,
        search: str = "",
        category: str = "All",
        status: str = "All",
    ) -> List[Dict[str, Any]]:
        """Fetches courses with optional filtering."""
        try:
            courses = CourseController.get_all_courses(
                search=search if search.strip() else None,
                category=category if category != "All" else None,
                status=status if status != "All" else None,
            )
            return [serialize_course(c) for c in courses]
        except Exception as e:
            logger.error(f"Error fetching courses: {e}")
            return []

    @Slot(str, result="QVariantMap")
    def getCourseById(self, course_id: str) -> Dict[str, Any]:
        """Fetches a single course by ID."""
        try:
            course = CourseController.get_course_by_id(course_id)
            return serialize_course(course)
        except Exception as e:
            logger.error(f"Error fetching course {course_id}: {e}")
            return {}

    @Slot(str, result="QVariantMap")
    def saveCourse(self, data_json: str) -> Dict[str, Any]:
        """Creates or updates a course in the catalog."""
        try:
            data = json.loads(data_json)
            course_id = data.get("id")

            if course_id:
                course = CourseController.update_course(course_id, data)
                if not course:
                    return {"success": False, "message": "Course not found", "id": ""}
                msg = f"Course {course.name} updated successfully."
                ret_id = str(course.id)
            else:
                course = CourseController.create_course(data)
                msg = f"Course {course.name} created with code {course.course_code}."
                ret_id = str(course.id)

            self.coursesChanged.emit()
            self.courseSaved.emit(True, msg, ret_id)
            return {"success": True, "message": msg, "id": ret_id}

        except Exception as e:
            logger.error(f"Error saving course: {e}")
            self.courseSaved.emit(False, str(e), "")
            return {"success": False, "message": str(e), "id": ""}

    @Slot(str, result=bool)
    def deleteCourse(self, course_id: str) -> bool:
        """Deletes a course from the catalog."""
        try:
            success = CourseController.delete_course(course_id)
            if success:
                self.coursesChanged.emit()
            return success
        except Exception as e:
            logger.error(f"Error deleting course {course_id}: {e}")
            return False

    @Slot(result="QVariantList")
    def getCategories(self) -> List[str]:
        """Returns distinct course categories."""
        try:
            courses = CourseController.get_all_courses()
            cats = sorted(list({c.category for c in courses if c.category}))
            return cats
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            return []

    @Slot(result="QVariantList")
    def getCourseNames(self) -> List[str]:
        """Returns names of all active courses for dropdown selectors."""
        try:
            courses = CourseController.get_all_courses(status="Active")
            return [c.name for c in courses if c.name]
        except Exception as e:
            logger.error(f"Error fetching course names: {e}")
            return []

    @Slot(str, result=float)
    def getStandardFeeForCourse(self, course_name: str) -> float:
        """Gets standard fee for a course name."""
        try:
            course = CourseController.get_course_by_name(course_name)
            if course:
                return float(course.standard_fee or 0.0)
            return 0.0
        except Exception as e:
            logger.error(f"Error looking up standard fee for {course_name}: {e}")
            return 0.0

    @Slot(result="QVariantMap")
    def getMetrics(self) -> Dict[str, Any]:
        """Fetches high-level metrics for the Courses module."""
        try:
            return CourseController.get_courses_dashboard_metrics()
        except Exception as e:
            logger.error(f"Error fetching course metrics: {e}")
            return {"total_courses": 0, "active_courses": 0, "avg_fee": 0.0, "categories_count": 0}

    @Slot(result=str)
    @Slot(str, result=str)
    def generateCourseCode(self, category: str = "") -> str:
        """Generates next sequential or category-specific course code."""
        try:
            return CourseController.generate_next_course_code(category if category else None)
        except Exception as e:
            logger.error(f"Error generating course code: {e}")
            return "CRS-01"

    @Slot(result=int)
    def seedDefaults(self) -> int:
        """Seeds default course catalog if empty."""
        try:
            seeded = CourseController.seed_default_courses_if_empty()
            if seeded > 0:
                self.coursesChanged.emit()
            return seeded
        except Exception as e:
            logger.error(f"Error seeding courses: {e}")
            return 0

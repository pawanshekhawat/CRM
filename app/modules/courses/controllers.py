import logging
from typing import Any, Dict, List, Optional
from sqlalchemy import func, or_

from app.core.database import get_db_session
from app.models.course import Course
from app.models.student import Student
from app.models.staff import Batch

logger = logging.getLogger("CRM.CourseController")

DEFAULT_COURSES_CATALOG = [
    {
        "course_code": "CRS-ARCH-01",
        "name": "Master Architecture",
        "category": "Architecture & Civil",
        "standard_fee": 120000.0,
        "description": "Complete architectural suite: AutoCAD 2D/3D, Revit Architecture, 3ds Max, V-Ray Rendering, Lumion, and BIM workflows.",
    },
    {
        "course_code": "CRS-INT-02",
        "name": "Interior Design",
        "category": "Interior Design",
        "standard_fee": 120000.0,
        "description": "Interior planning, space management, SketchUp, 3ds Max, Lighting, Material Texturing & Photorealistic Renderings.",
    },
    {
        "course_code": "CRS-DS-03",
        "name": "Data Science",
        "category": "Data & AI",
        "standard_fee": 75000.0,
        "description": "Python, Machine Learning, Deep Learning, Statistics, NLP, Scikit-Learn, TensorFlow, and Data Visualization.",
    },
    {
        "course_code": "CRS-FS-04",
        "name": "Full Stack Web Development",
        "category": "IT & Programming",
        "standard_fee": 71000.0,
        "description": "Comprehensive MERN/Python Stack: HTML5, CSS3, JavaScript, React, Node.js, Express, Databases & Cloud Deployments.",
    },
    {
        "course_code": "CRS-LS-05",
        "name": "Land Survey",
        "category": "Civil & Survey",
        "standard_fee": 70000.0,
        "description": "Practical Total Station surveying, AutoLevel, GPS/DGPS, Contouring, Topographic mapping, and Survey AutoCAD plotting.",
    },
    {
        "course_code": "CRS-DFT-06",
        "name": "Draftsman (Civil / Mechanical)",
        "category": "Drafting & CAD",
        "standard_fee": 45500.0,
        "description": "Engineering drawings, 2D/3D AutoCAD drafting, building sanction drawings, structural layouts, and isometric projections.",
    },
    {
        "course_code": "CRS-MPD-07",
        "name": "Mechanical Product Design",
        "category": "Mechanical & Design",
        "standard_fee": 45500.0,
        "description": "3D CAD Modeling in SolidWorks/CATIA, product surfacing, GD&T, mechanical assemblies, and product detailing.",
    },
    {
        "course_code": "CRS-CNC-08",
        "name": "Product Design & CNC Machine",
        "category": "Mechanical & Design",
        "standard_fee": 45500.0,
        "description": "3D CAD Modeling in SolidWorks/CATIA, MasterCAM CNC programming, toolpath generation, and G/M code verification.",
    },
    {
        "course_code": "CRS-VID-09",
        "name": "Video Editing",
        "category": "Multimedia & Graphics",
        "standard_fee": 45500.0,
        "description": "Professional non-linear video editing, Adobe Premiere Pro, After Effects VFX, audio mastering, color grading, and reels production.",
    },
    {
        "course_code": "CRS-DA-09",
        "name": "Data Analytics",
        "category": "Data & AI",
        "standard_fee": 45000.0,
        "description": "Business intelligence: Advanced Excel, SQL database queries, Power BI, Tableau interactive dashboards, and Python analysis.",
    },
    {
        "course_code": "CRS-DCA-10",
        "name": "DCA (Diploma in Computer Applications)",
        "category": "Computer Applications",
        "standard_fee": 35500.0,
        "description": "Computer Fundamentals, Windows OS, MS Office Suite (Word/Excel/PPT), Internet, Tally Prime, and basic programming logic.",
    },
    {
        "course_code": "CRS-WEB-11",
        "name": "Web Design",
        "category": "IT & Programming",
        "standard_fee": 35500.0,
        "description": "UI/UX fundamentals, Figma wireframing, responsive layouts, HTML5, CSS3, Tailwind CSS, JavaScript, and modern web interfaces.",
    },
    {
        "course_code": "CRS-DM-12",
        "name": "Digital Marketing",
        "category": "Digital Marketing",
        "standard_fee": 35500.0,
        "description": "SEO, Google Search & Display Ads, Meta Ads (Facebook/Instagram), Social Media Management, Content Marketing & Analytics.",
    },
    {
        "course_code": "CRS-GD-13",
        "name": "Graphic Design",
        "category": "Multimedia & Graphics",
        "standard_fee": 35000.0,
        "description": "Brand identity, Adobe Photoshop, Adobe Illustrator, CorelDRAW, typography, poster design, logo crafting, and print media.",
    },
    {
        "course_code": "CRS-C3D-14",
        "name": "Civil 3D",
        "category": "Architecture & Civil",
        "standard_fee": 35000.0,
        "description": "AutoCAD Civil 3D for corridor modeling, highway alignments, grading plans, surface modeling, and pipe networks.",
    },
    {
        "course_code": "CRS-TLY-15",
        "name": "Tally Prime / ERP",
        "category": "Accounting & Finance",
        "standard_fee": 25500.0,
        "description": "Computerized accounting, GST billing, E-way bill generation, TDS, Payroll management, and Financial Statement finalization.",
    },
    {
        "course_code": "CRS-BSC-16",
        "name": "Basic Computer",
        "category": "Foundational IT",
        "standard_fee": 7500.0,
        "description": "Basic computer operations, keyboard typing skills, MS Word formatting, Excel basics, PowerPoint presentations, and safe browsing.",
    },
    {
        "course_code": "CRS-CAD-17",
        "name": "AutoCAD",
        "category": "Architecture & Civil",
        "standard_fee": 20000.0,
        "description": "Professional 2D drafting, geometric layouts, layers, dimensioning, isometric drawings, 3D modeling, and plotting.",
    },
    {
        "course_code": "CRS-FED-18",
        "name": "Frontend Development",
        "category": "IT & Programming",
        "standard_fee": 35000.0,
        "description": "HTML5, CSS3, Modern JavaScript (ES6+), React.js, Tailwind CSS, Responsive Design, State Management, and Frontend API Integrations.",
    },
]




class CourseController:
    """Business logic and database transactions for the Course Catalog."""

    @staticmethod
    def generate_next_course_code() -> str:
        """Generates a sequential course code."""
        with get_db_session() as session:
            count = session.query(func.count(Course.id)).scalar() or 0
            return f"CRS-{(count + 1):03d}"

    @staticmethod
    def seed_default_courses_if_empty() -> int:
        """Seeds or syncs the standard course catalog in the database."""
        with get_db_session() as session:
            seeded = 0
            for item in DEFAULT_COURSES_CATALOG:
                # Check for exact or alias match (e.g. Master in Architecture vs Master Architecture)
                existing = session.query(Course).filter(
                    or_(
                        Course.name.ilike(item["name"].strip()),
                        Course.course_code == item["course_code"],
                    )
                ).first()

                if not existing and item["name"] == "Master Architecture":
                    existing = session.query(Course).filter(Course.name.ilike("Master in Architecture")).first()

                if not existing:
                    course = Course(
                        course_code=item["course_code"],
                        name=item["name"],
                        category=item["category"],
                        standard_fee=item["standard_fee"],
                        description=item["description"],
                        status="Active",
                    )
                    session.add(course)
                    seeded += 1
                else:
                    # Ensure standard pricing and normalized naming is up to date
                    existing.name = item["name"]
                    existing.standard_fee = item["standard_fee"]
                    existing.category = item["category"]
                    existing.description = item["description"]

            session.commit()
            if seeded > 0:
                logger.info(f"Seeded {seeded} new standard courses into database catalog.")
            return seeded

    @staticmethod
    def get_all_courses(
        search: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Course]:
        """Fetches all courses with optional filters."""
        with get_db_session() as session:
            query = session.query(Course)

            if search:
                term = f"%{search.strip()}%"
                query = query.filter(
                    or_(
                        Course.name.ilike(term),
                        Course.course_code.ilike(term),
                        Course.category.ilike(term),
                        Course.description.ilike(term),
                    )
                )

            if category and category != "All":
                query = query.filter(Course.category == category)

            if status and status != "All":
                query = query.filter(Course.status == status)

            courses = query.order_by(Course.standard_fee.desc(), Course.name.asc()).all()
            session.expunge_all()
            return courses

    @staticmethod
    def get_course_by_id(course_id: str) -> Optional[Course]:
        """Fetches a single course by ID."""
        with get_db_session() as session:
            course = session.query(Course).filter(Course.id == course_id).first()
            if course:
                session.expunge_all()
            return course

    @staticmethod
    def get_course_by_name(name: str) -> Optional[Course]:
        """Fetches a course by exact or close name match."""
        if not name:
            return None
        clean_name = name.strip()
        with get_db_session() as session:
            course = session.query(Course).filter(Course.name.ilike(clean_name)).first()
            if not course:
                # Handle common aliases
                if clean_name.lower() in ["master architecture", "master in architecture", "architecture", "master architect", "master-archi"]:
                    course = session.query(Course).filter(Course.name.ilike("Master Architecture")).first()
                elif clean_name.lower() in ["cnc", "cnc design", "product design", "product design & cnc machine"]:
                    course = session.query(Course).filter(Course.name.ilike("Product Design & CNC Machine")).first()
                elif clean_name.lower() in ["land survey", "total station land survey"]:
                    course = session.query(Course).filter(Course.name.ilike("Land Survey")).first()
            if course:
                session.expunge_all()
            return course

    @staticmethod
    def create_course(data: Dict[str, Any]) -> Course:
        """Creates a new course program."""
        with get_db_session() as session:
            code = data.get("course_code") or CourseController.generate_next_course_code()
            course = Course(
                course_code=code.strip(),
                name=data["name"].strip(),
                category=data.get("category", "General").strip() if data.get("category") else None,
                standard_fee=float(data.get("standard_fee") or 0.0),
                description=data.get("description", "").strip() if data.get("description") else None,
                status=data.get("status", "Active"),
            )
            session.add(course)
            session.flush()
            target_id = course.id
            session.commit()
            logger.info(f"Created course: {course.name} ({course.course_code})")

        return CourseController.get_course_by_id(target_id)

    @staticmethod
    def update_course(course_id: str, data: Dict[str, Any]) -> Optional[Course]:
        """Updates an existing course."""
        with get_db_session() as session:
            course = session.query(Course).filter(Course.id == course_id).first()
            if not course:
                return None

            for field in ["course_code", "name", "category", "standard_fee", "description", "status"]:
                if field in data:
                    if field == "standard_fee":
                        setattr(course, field, float(data[field] or 0.0))
                    else:
                        setattr(course, field, data[field])

            session.commit()
            logger.info(f"Updated course: {course.name} ({course.course_code})")

        return CourseController.get_course_by_id(course_id)

    @staticmethod
    def delete_course(course_id: str) -> bool:
        """Deletes a course from the catalog."""
        with get_db_session() as session:
            course = session.query(Course).filter(Course.id == course_id).first()
            if not course:
                return False

            session.delete(course)
            session.commit()
            logger.info(f"Deleted course ID: {course_id}")
            return True

    @staticmethod
    def get_course_stats(course_name: str) -> Dict[str, int]:
        """Calculates active students and batch counts for a specific course."""
        with get_db_session() as session:
            term = f"%{course_name.strip()}%"
            student_count = session.query(func.count(Student.id)).filter(Student.course_name.ilike(term)).scalar() or 0
            batch_count = session.query(func.count(Batch.id)).filter(Batch.course_name.ilike(term)).scalar() or 0
            return {
                "student_count": student_count,
                "batch_count": batch_count,
            }

    @staticmethod
    def get_courses_dashboard_metrics() -> Dict[str, Any]:
        """Calculates overall metrics for Courses catalog."""
        with get_db_session() as session:
            total_courses = session.query(func.count(Course.id)).scalar() or 0
            active_courses = session.query(func.count(Course.id)).filter(Course.status == "Active").scalar() or 0
            avg_fee = session.query(func.avg(Course.standard_fee)).scalar() or 0.0
            categories_count = session.query(func.count(func.distinct(Course.category))).scalar() or 0

            return {
                "total_courses": total_courses,
                "active_courses": active_courses,
                "avg_fee": avg_fee,
                "categories_count": categories_count,
            }

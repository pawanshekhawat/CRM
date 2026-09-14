import logging
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import DATABASE_URL, DATABASE_PATH, LOGS_DIR
from app.core.base import Base

# Configure logger
logger = logging.getLogger("CRM.Database")

# Create SQLite Engine
# Enable foreign keys and configure journal strategy
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    # Enable Foreign Key Constraints in SQLite
    cursor.execute("PRAGMA foreign_keys=ON")
    # For portable USB, WAL mode with synchronous=NORMAL ensures high performance and data safety
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}", exc_info=True)
        raise
    finally:
        session.close()

def init_db():
    """Create all database tables and perform lightweight schema updates."""
    # Import all models so metadata knows about them
    import app.models.student  # noqa: F401
    import app.models.custom_fields  # noqa: F401
    import app.models.staff  # noqa: F401
    import app.models.course  # noqa: F401
    import app.models.message_template  # noqa: F401

    Base.metadata.create_all(bind=engine)

    # Lightweight automatic schema migration for SQLite
    try:
        with engine.begin() as conn:
            # Check students table columns
            res = conn.exec_driver_sql("PRAGMA table_info(students)").fetchall()
            existing_cols = {row[1] for row in res}
            if existing_cols and "assigned_staff_id" not in existing_cols:
                conn.exec_driver_sql("ALTER TABLE students ADD COLUMN assigned_staff_id VARCHAR(36) REFERENCES staff(id) ON DELETE SET NULL")
            if existing_cols and "admission_form_path" not in existing_cols:
                conn.exec_driver_sql("ALTER TABLE students ADD COLUMN admission_form_path VARCHAR(255)")
            if existing_cols and "referred_by_student_id" not in existing_cols:
                conn.exec_driver_sql("ALTER TABLE students ADD COLUMN referred_by_student_id VARCHAR(36) REFERENCES students(id) ON DELETE SET NULL")
            if existing_cols and "referral_discount" not in existing_cols:
                conn.exec_driver_sql("ALTER TABLE students ADD COLUMN referral_discount FLOAT DEFAULT 0.0")
            if existing_cols and "referral_commission" not in existing_cols:
                conn.exec_driver_sql("ALTER TABLE students ADD COLUMN referral_commission FLOAT DEFAULT 0.0")
    except Exception as e:
        logger.warning(f"Schema migration note: {e}")

    # Seed default courses if catalog is empty
    try:
        from app.modules.courses.controllers import CourseController
        CourseController.seed_default_courses_if_empty()
    except Exception as e:
        logger.warning(f"Default courses seeding note: {e}")

    # Seed default real staff members if directory is empty
    try:
        from app.modules.staff.controllers import StaffController
        StaffController.seed_default_staff_if_empty()
    except Exception as e:
        logger.warning(f"Default staff seeding note: {e}")

    logger.info(f"Database initialized successfully at {DATABASE_PATH}")

def close_db():
    """Checkpoint WAL and dispose engine cleanly on application shutdown."""
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql("PRAGMA wal_checkpoint(TRUNCATE);")
        engine.dispose()
        logger.info("Database cleanly closed and checkpointed.")
    except Exception as e:
        logger.warning(f"Error during clean database shutdown: {e}")

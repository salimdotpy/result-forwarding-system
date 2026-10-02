from sqlmodel import Session, SQLModel, create_engine
from app.core.config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url, echo=False, pool_pre_ping=True)


def init_db() -> None:
    from app.models import (  # noqa: F401
        User, Faculty, Department, Course, Student, ResultSubmission,
        ResultRecord, WorkflowEvent, Notification, AuditLog,
    )
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

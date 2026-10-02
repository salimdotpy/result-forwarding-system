from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel
from app.models.enums import ResultStatus, Semester


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ResultSubmission(SQLModel, table=True):
    __tablename__ = "result_submissions"
    id: Optional[int] = Field(default=None, primary_key=True)
    reference: str = Field(index=True, max_length=40, unique=True)
    academic_session: str = Field(index=True, max_length=20)
    semester: Semester = Field(index=True)
    faculty_id: int = Field(foreign_key="faculties.id", index=True)
    department_id: int = Field(foreign_key="departments.id", index=True)
    course_id: int = Field(foreign_key="courses.id", index=True)
    lecturer_id: int = Field(foreign_key="users.id", index=True)
    status: ResultStatus = Field(default=ResultStatus.DRAFT, index=True)
    submitted_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    records: list["ResultRecord"] = Relationship(back_populates="submission", cascade_delete=True)


class ResultRecord(SQLModel, table=True):
    __tablename__ = "result_records"
    id: Optional[int] = Field(default=None, primary_key=True)
    submission_id: int = Field(foreign_key="result_submissions.id", index=True)
    student_id: Optional[int] = Field(default=None, foreign_key="students.id", index=True)
    matric_number: str = Field(index=True, max_length=60)
    student_name: str = Field(max_length=150)
    score: Decimal = Field(max_digits=6, decimal_places=2)
    grade: Optional[str] = Field(default=None, max_length=5)
    remark: Optional[str] = Field(default=None, max_length=100)
    submission: Optional[ResultSubmission] = Relationship(back_populates="records")


class WorkflowEvent(SQLModel, table=True):
    __tablename__ = "workflow_events"
    id: Optional[int] = Field(default=None, primary_key=True)
    submission_id: int = Field(foreign_key="result_submissions.id", index=True)
    actor_id: int = Field(foreign_key="users.id", index=True)
    action: str = Field(max_length=100)
    previous_status: Optional[ResultStatus] = None
    new_status: ResultStatus
    comment: Optional[str] = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=utcnow, index=True)

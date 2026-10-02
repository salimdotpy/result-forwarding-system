from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Notification(SQLModel, table=True):
    __tablename__ = "notifications"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    submission_id: Optional[int] = Field(default=None, foreign_key="result_submissions.id", index=True)
    title: str = Field(max_length=160)
    message: str = Field(max_length=500)
    is_read: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=utcnow, index=True)


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    role: Optional[str] = Field(default=None, max_length=40)
    action: str = Field(index=True, max_length=120)
    submission_id: Optional[int] = Field(default=None, foreign_key="result_submissions.id", index=True)
    previous_status: Optional[str] = Field(default=None, max_length=60)
    new_status: Optional[str] = Field(default=None, max_length=60)
    comment: Optional[str] = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=utcnow, index=True)

from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel
from app.models.enums import UserRole


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str = Field(max_length=150)
    email: str = Field(index=True, max_length=190, unique=True)
    password_hash: str = Field(max_length=255)
    role: UserRole = Field(default=UserRole.LECTURER, index=True)
    is_active: bool = Field(default=True, index=True)
    faculty_id: Optional[int] = Field(default=None, foreign_key="faculties.id", index=True)
    department_id: Optional[int] = Field(default=None, foreign_key="departments.id", index=True)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

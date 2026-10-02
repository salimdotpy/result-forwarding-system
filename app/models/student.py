from typing import Optional
from sqlmodel import Field, SQLModel


class Student(SQLModel, table=True):
    __tablename__ = "students"
    id: Optional[int] = Field(default=None, primary_key=True)
    matric_number: str = Field(index=True, max_length=60, unique=True)
    full_name: str = Field(index=True, max_length=150)
    department_id: int = Field(foreign_key="departments.id", index=True)

from typing import Optional
from sqlmodel import Field, Relationship, SQLModel


class Faculty(SQLModel, table=True):
    __tablename__ = "faculties"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=150, unique=True)
    code: str = Field(index=True, max_length=30, unique=True)
    departments: list["Department"] = Relationship(back_populates="faculty")


class Department(SQLModel, table=True):
    __tablename__ = "departments"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=150)
    code: str = Field(index=True, max_length=30, unique=True)
    faculty_id: int = Field(foreign_key="faculties.id", index=True)
    faculty: Optional[Faculty] = Relationship(back_populates="departments")
    courses: list["Course"] = Relationship(back_populates="department")


class Course(SQLModel, table=True):
    __tablename__ = "courses"
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, max_length=30, unique=True)
    title: str = Field(max_length=200)
    units: int = Field(default=3, ge=1, le=10)
    department_id: int = Field(foreign_key="departments.id", index=True)
    department: Optional[Department] = Relationship(back_populates="courses")

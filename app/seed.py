from sqlmodel import Session, select
from app.db.session import engine, init_db
from app.core.security import hash_password
from app.models import Faculty, Department, Course, Student, User, ResultSubmission, ResultRecord, WorkflowEvent, Notification, AuditLog
from app.models.enums import UserRole, Semester, ResultStatus, WorkflowAction
from app.services.audit import log_audit

DEMO_PASSWORD = "1234"


def get_or_create(session, model, **kwargs):
    statement = select(model)
    for key, value in kwargs.items():
        statement = statement.where(getattr(model, key) == value)
    item = session.exec(statement).first()
    if item:
        return item
    item = model(**kwargs)
    session.add(item); session.flush()
    return item


def seed():
    init_db()
    with Session(engine) as session:
        faculty = get_or_create(session, Faculty, code="SCT", name="School of Computing Technology")
        department = get_or_create(session, Department, code="CS", name="Department of Computer Science", faculty_id=faculty.id)
        course = get_or_create(session, Course, code="COM 112", title="Introduction to Digital Electronics", units=3, department_id=department.id)
        for i in range(1, 9):
            get_or_create(session, Student, matric_number=f"{department.code}20250101{i:03}", full_name=["Amina Yusuf", "Daniel Okafor", "DIYAOLU RAHMON".title(), "Ifeanyi Nwosu", "Mary Johnson", "Samuel Ade", "Fatima Bello", "David Obi", "Grace Musa"][i-1], department_id=department.id)

        accounts = [
            ("System Administrator", "admin@gmail.com", UserRole.ADMIN, None, None),
            ("Aisha Lecturer", "lecturer@gmail.com", UserRole.LECTURER, faculty.id, department.id),
            ("Michael Examination Officer", "examofficer@gmail.com", UserRole.EXAMINATION_OFFICER, faculty.id, department.id),
            ("Mr. Ramoni T.A. HOD", "hod@gmail.com", UserRole.HOD, faculty.id, department.id),
            ("Prof. Grace Dean", "dean@gmail.com", UserRole.DEAN, faculty.id, None),
            ("Academic Planning Officer", "planning@gmail.com", UserRole.ACADEMIC_PLANNING, None, None),
        ]
        users = {}
        for name, email, role, faculty_id, department_id in accounts:
            user = session.exec(select(User).where(User.email == email)).first()
            if not user:
                user = User(full_name=name, email=email, password_hash=hash_password(DEMO_PASSWORD), role=role, faculty_id=faculty_id, department_id=department_id)
                session.add(user); session.flush()
            users[role] = user

        if not session.exec(select(ResultSubmission)).first():
            demo = ResultSubmission(reference="RES-DEMO001", academic_session="2025/2026", semester=Semester.FIRST, faculty_id=faculty.id, department_id=department.id, course_id=course.id, lecturer_id=users[UserRole.LECTURER].id, status=ResultStatus.VERIFIED)
            session.add(demo); session.flush()
            students = session.exec(select(Student).limit(5)).all()
            for idx, student in enumerate(students):
                session.add(ResultRecord(submission_id=demo.id, student_id=student.id, matric_number=student.matric_number, student_name=student.full_name, score=Decimal(62 + idx * 5), grade=["BC", "B", "AB", "A", "A"][idx], remark="Satisfactory"))
            for actor, action, old, new in [
                (users[UserRole.LECTURER], WorkflowAction.SUBMITTED.value, ResultStatus.DRAFT, ResultStatus.SUBMITTED),
                (users[UserRole.EXAMINATION_OFFICER], WorkflowAction.START_VERIFICATION.value, ResultStatus.SUBMITTED, ResultStatus.UNDER_VERIFICATION),
                (users[UserRole.EXAMINATION_OFFICER], WorkflowAction.VERIFIED.value, ResultStatus.UNDER_VERIFICATION, ResultStatus.VERIFIED),
            ]:
                session.add(WorkflowEvent(submission_id=demo.id, actor_id=actor.id, action=action, previous_status=old, new_status=new))
                log_audit(session, user=actor, action=action, submission_id=demo.id, previous_status=old.value, new_status=new.value)
            session.add(Notification(user_id=users[UserRole.HOD].id, submission_id=demo.id, title="Result awaiting HOD approval", message="RES-DEMO001 has been verified and is ready for review."))
        session.commit()
        print("Seed complete. Demo password for all accounts:", DEMO_PASSWORD)
        for role, user in users.items():
            print(f"{role.value:22} {user.email}")


if __name__ == "__main__":
    from decimal import Decimal
    seed()

from sqlmodel import Session, select
from app.models import Notification, User
from app.models.enums import UserRole


def notify(session: Session, user_id: int, title: str, message: str, submission_id: int | None = None) -> None:
    session.add(Notification(user_id=user_id, title=title, message=message, submission_id=submission_id))


def notify_role(session: Session, role: UserRole, title: str, message: str, submission_id: int | None = None, department_id: int | None = None, faculty_id: int | None = None) -> None:
    statement = select(User).where(User.role == role, User.is_active == True)  # noqa: E712
    if department_id is not None:
        statement = statement.where(User.department_id == department_id)
    if faculty_id is not None:
        statement = statement.where(User.faculty_id == faculty_id)
    for user in session.exec(statement).all():
        notify(session, user.id, title, message, submission_id)

from sqlmodel import Session
from app.models import AuditLog, User


def log_audit(
    session: Session,
    *,
    user: User | None,
    action: str,
    submission_id: int | None = None,
    previous_status: str | None = None,
    new_status: str | None = None,
    comment: str | None = None,
) -> None:
    session.add(AuditLog(
        user_id=user.id if user else None,
        role=user.role.value if user else None,
        action=action,
        submission_id=submission_id,
        previous_status=previous_status,
        new_status=new_status,
        comment=comment,
    ))

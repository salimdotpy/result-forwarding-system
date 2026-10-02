from collections import Counter
from fastapi import APIRouter, Depends, Request
from sqlmodel import Session, select, func
from app.core.dependencies import SessionDep, current_user
from app.models import ResultSubmission, Notification, User
from app.models.enums import ResultStatus
from app.core.templates import templates, template_context

router = APIRouter()

@router.get("/dashboard")
async def dashboard(request: Request, session: SessionDep, user: User = Depends(current_user)):
    base = select(ResultSubmission)
    if user.role.value == "lecturer":
        base = base.where(ResultSubmission.lecturer_id == user.id)
    elif user.role.value in {"examination_officer", "hod"}:
        base = base.where(ResultSubmission.department_id == user.department_id)
    elif user.role.value == "dean":
        base = base.where(ResultSubmission.faculty_id == user.faculty_id)
    items = session.exec(base.order_by(ResultSubmission.updated_at.desc()).limit(8)).all()
    all_rows = session.exec(base).all()
    counts = Counter(row.status for row in all_rows)
    unread = session.exec(select(func.count(Notification.id)).where(Notification.user_id == user.id, Notification.is_read == False)).one()  # noqa: E712
    return templates.TemplateResponse(request=request, name="dashboard/index.html", context=template_context(request, user=user, items=items, counts=counts, unread=unread))

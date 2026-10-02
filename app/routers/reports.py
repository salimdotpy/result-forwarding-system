import csv
import io
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlmodel import select
from app.core.dependencies import SessionDep, current_user
from app.models import Department, Faculty, ResultSubmission, User
from app.models.enums import UserRole
from app.core.templates import templates, template_context

router = APIRouter(prefix="/reports")


def scoped(session, user: User):
    q = select(ResultSubmission)
    if user.role == UserRole.LECTURER: q = q.where(ResultSubmission.lecturer_id == user.id)
    elif user.role in {UserRole.EXAMINATION_OFFICER, UserRole.HOD}: q = q.where(ResultSubmission.department_id == user.department_id)
    elif user.role == UserRole.DEAN: q = q.where(ResultSubmission.faculty_id == user.faculty_id)
    return q

@router.get("")
async def reports(request: Request, session: SessionDep, user: User = Depends(current_user), status_filter: str = ""):
    q = scoped(session, user)
    if status_filter: q = q.where(ResultSubmission.status == status_filter)
    rows = session.exec(q.order_by(ResultSubmission.updated_at.desc())).all()
    return templates.TemplateResponse(request=request, name="reports/index.html", context=template_context(request, user=user, rows=rows, status_filter=status_filter))

@router.get("/export.csv")
async def export_csv(session: SessionDep, user: User = Depends(current_user), status_filter: str = ""):
    q = scoped(session, user)
    if status_filter: q = q.where(ResultSubmission.status == status_filter)
    rows = session.exec(q.order_by(ResultSubmission.updated_at.desc())).all()
    out = io.StringIO(); writer = csv.writer(out)
    writer.writerow(["Reference", "Academic Session", "Semester", "Faculty ID", "Department ID", "Course ID", "Lecturer ID", "Status", "Submitted At"])
    for row in rows:
        writer.writerow([row.reference, row.academic_session, row.semester.value, row.faculty_id, row.department_id, row.course_id, row.lecturer_id, row.status.value, row.submitted_at.isoformat() if row.submitted_at else ""])
    return StreamingResponse(iter([out.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=result-forwarding-report.csv"})

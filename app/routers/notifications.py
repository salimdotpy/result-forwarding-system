from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlmodel import select
from app.core.dependencies import SessionDep, current_user
from app.models import Notification, User
from app.core.templates import templates, template_context

router = APIRouter(prefix="/notifications")

@router.get("")
async def notifications_page(request: Request, session: SessionDep, user: User = Depends(current_user)):
    rows = session.exec(select(Notification).where(Notification.user_id == user.id).order_by(Notification.created_at.desc()).limit(100)).all()
    return templates.TemplateResponse(request=request, name="notifications/index.html", context=template_context(request, user=user, rows=rows))

@router.post("/{notification_id}/read")
async def mark_read(notification_id: int, session: SessionDep, user: User = Depends(current_user)):
    item = session.get(Notification, notification_id)
    if item and item.user_id == user.id:
        item.is_read = True; session.add(item); session.commit()
    return RedirectResponse("/notifications", status_code=303)

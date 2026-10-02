from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import select
from app.core.dependencies import SessionDep, require_roles
from app.core.security import hash_password
from app.models import AuditLog, Department, Faculty, User
from app.models.enums import UserRole
from app.core.templates import templates, template_context

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users")
async def users(request: Request, session: SessionDep, user: User = Depends(require_roles(UserRole.ADMIN))):
    rows = session.exec(select(User).order_by(User.full_name)).all()
    faculties = session.exec(select(Faculty).order_by(Faculty.name)).all()
    departments = session.exec(select(Department).order_by(Department.name)).all()
    return templates.TemplateResponse(request=request, name="admin/users.html", context=template_context(request, user=user, rows=rows, faculties=faculties, departments=departments, roles=list(UserRole)))

@router.post("/users")
async def create_user(request: Request, session: SessionDep, user: User = Depends(require_roles(UserRole.ADMIN)), full_name: str = Form(...), email: str = Form(...), password: str = Form(...), role: UserRole = Form(...), faculty_id: int | None = Form(None), department_id: int | None = Form(None)):
    email = email.strip().lower()
    if session.exec(select(User).where(User.email == email)).first():
        raise HTTPException(409, "A user with that email already exists.")
    new_user = User(full_name=full_name.strip(), email=email, password_hash=hash_password(password), role=role, faculty_id=faculty_id, department_id=department_id)
    session.add(new_user); session.commit()
    return RedirectResponse(request=request, name="/admin/users", status_code=303)

@router.post("/users/{user_id}/toggle")
async def toggle_user(request: Request, user_id: int, session: SessionDep, user: User = Depends(require_roles(UserRole.ADMIN))):
    target = session.get(User, user_id)
    if not target: raise HTTPException(404, "The requested user could not be found.")
    if target.id == user.id: raise HTTPException(422, "You cannot deactivate your own account.")
    target.is_active = not target.is_active; target.updated_at = datetime.now(timezone.utc)
    session.add(target); session.commit()
    return RedirectResponse(request=request, name="/admin/users", status_code=303)

@router.get("/organization")
async def organization(request: Request, session: SessionDep, user: User = Depends(require_roles(UserRole.ADMIN))):
    return templates.TemplateResponse(request=request, name="admin/organization.html", context=template_context(request, user=user, faculties=session.exec(select(Faculty)).all(), departments=session.exec(select(Department)).all()))

@router.post("/faculties")
async def create_faculty(session: SessionDep, user: User = Depends(require_roles(UserRole.ADMIN)), name: str = Form(...), code: str = Form(...)):
    session.add(Faculty(name=name.strip(), code=code.strip().upper())); session.commit(); return RedirectResponse("/admin/organization", status_code=303)

@router.post("/departments")
async def create_department(session: SessionDep, user: User = Depends(require_roles(UserRole.ADMIN)), name: str = Form(...), code: str = Form(...), faculty_id: int = Form(...)):
    session.add(Department(name=name.strip(), code=code.strip().upper(), faculty_id=faculty_id)); session.commit(); return RedirectResponse("/admin/organization", status_code=303)

@router.get("/audit")
async def audit(request: Request, session: SessionDep, user: User = Depends(require_roles(UserRole.ADMIN))):
    rows = session.exec(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(250)).all()
    return templates.TemplateResponse(request=request, name="admin/audit.html", context=template_context(request, user=user, rows=rows))

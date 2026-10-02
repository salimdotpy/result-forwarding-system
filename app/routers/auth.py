from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from sqlmodel import select
from app.core.dependencies import SessionDep
from app.core.security import verify_password
from app.models import User
from app.core.templates import templates, template_context

router = APIRouter()

@router.get("/login")
async def login_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse(request=request, name="auth/login.html", context=template_context(request))

@router.post("/login")
async def login(request: Request, session: SessionDep, email: str = Form(...), password: str = Form(...)):
    user = session.exec(select(User).where(User.email == email.strip().lower())).first()
    if not user or not user.is_active or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(request=request, name="auth/login.html", context=template_context(request, error="Invalid email or password."), status_code=401)
    request.session.clear()
    request.session["user_id"] = user.id
    request.session["role"] = user.role.value
    return RedirectResponse("/dashboard", status_code=303)

@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)

import logging
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import get_settings
from app.core.templates import templates, template_context
from app.db.session import init_db
from app.routers import auth, dashboard, results, admin, reports, notifications

BASE_DIR = Path(__file__).resolve().parent
settings = get_settings()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("result_forwarding")

app = FastAPI(title=settings.app_name)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, session_cookie=settings.session_cookie, max_age=60 * 60 * 8, same_site="lax", https_only=settings.app_env == "production")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(results.router)
app.include_router(admin.router)
app.include_router(reports.router)
app.include_router(notifications.router)

@app.on_event("startup")
def startup():
    init_db()

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code in {303, 307, 308}:
        return RedirectResponse(exc.headers.get("Location", "/"), status_code=exc.status_code)
    if exc.status_code == 403:
        return templates.TemplateResponse(request=request, name="errors/403.html", context=template_context(request), status_code=403)
    if exc.status_code == 404:
        return templates.TemplateResponse(request=request, name="errors/404.html", context=template_context(request), status_code=404)
    return templates.TemplateResponse(request=request, name="errors/error.html", context=template_context(request, message=exc.detail or "Something went wrong. Please try again."), status_code=exc.status_code)

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled application error", exc_info=exc)
    return templates.TemplateResponse(request=request, name="errors/500.html", context=template_context(request), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.get("/", include_in_schema=False)
async def root(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/dashboard", status_code=303)
    return RedirectResponse("/login", status_code=303)

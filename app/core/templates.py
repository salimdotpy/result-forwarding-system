from pathlib import Path
from fastapi import Request
from starlette.templating import Jinja2Templates
from app.core.config import get_settings

BASE_DIR = Path(__file__).resolve().parents[1]
settings = get_settings()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

def template_context(request: Request, **kwargs):
    return {"request": request, "app_name": "settings.app_name", "config": "settings", **kwargs}

templates.env.globals["app_name"] = settings.app_name
templates.env.filters["role_label"] = lambda value: value.replace("_", " ").title() if value else ""
templates.env.globals["status_classes"] = lambda status: {
    "Draft": "badge-ghost", "Submitted": "badge-info", "Under Verification": "badge-warning",
    "Returned for Correction": "badge-error", "Verified": "badge-success", "HOD Approved": "badge-primary",
    "Dean Approved": "badge-primary", "Forwarded": "badge-accent", "Received": "badge-success", "Rejected": "badge-error",
}.get(str(status), "badge-neutral")

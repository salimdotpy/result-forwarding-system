from typing import Annotated
from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session
from app.db.session import get_session
from app.models import User
from app.models.enums import UserRole

SessionDep = Annotated[Session, Depends(get_session)]


def current_user(request: Request, session: SessionDep) -> User:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})
    user = session.get(User, int(user_id))
    if not user or not user.is_active:
        request.session.clear()
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})
    return user


def require_roles(*roles: UserRole):
    def dependency(user: Annotated[User, Depends(current_user)]) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="You do not have permission to perform this action.")
        return user
    return dependency

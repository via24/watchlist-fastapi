from typing import Any, Dict

from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager
from sqlalchemy import select

from .config import settings
from .database import SessionLocal
from .models import User, Movie

SECRET = settings.secret_key
manager = LoginManager(
    SECRET,
    "/login",
    use_cookie=True,
    use_header=False,
)


def inject_user(request: Request) -> Dict[str, Any]:
    msg = request.state.msg if hasattr(request.state, "msg") else None
    # print(">>>>>>>>>>>>>>>>", msg)
    with SessionLocal() as ses:
        user = ses.execute(select(User.name)).one()
        movies = ses.execute(select(Movie)).scalars().all()
    return {"user": user, "movies": movies, "msg": msg}


# 模版
templates = Jinja2Templates(directory="templates", context_processors=[inject_user])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

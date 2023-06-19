from typing import Callable

from fastapi import FastAPI, Request, Depends, Form
from fastapi.staticfiles import StaticFiles
from sqlalchemy import update
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse, Response

from .dependencies import get_db, templates, manager
from .models import Movie, User
from .routers import movie, auth

app = FastAPI()
manager.useRequest(app)
app.include_router(auth.router)
app.include_router(movie.router)

# 静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")
app_session: dict[str, str] = {}


@app.middleware("http")
async def cookie_middleware(
    request: Request, call_next: Callable
) -> JSONResponse | Response:
    in_token = request.cookies.get("access-token")
    if in_token:
        if in_token not in app_session.values():
            # 无效token
            return JSONResponse({"detail": "Invalid Credentials"}, status_code=401)
        current_user = await manager.get_current_user(in_token)

    response: Response = await call_next(request)
    # 当设置cookie时
    if ck := response.headers.get("Set-Cookie"):
        # 清除cookie
        if (out_token := ck.split("; ")[0].split("=")[1]) == '""':
            app_session.pop(current_user.email)
        else:
            # 设置cookie
            current_user = await manager.get_current_user(out_token)
            app_session[current_user.email] = out_token

    return response


@app.exception_handler(404)  # 404
async def not_found_exception_handler(request, exc):
    return templates.TemplateResponse("404.html", {"request": request}, 404)


@app.api_route("/", methods=["GET", "POST"])
def index(
    request: Request,
    title: str = Form(default=None),
    year: str = Form(default=None),
    db: Session = Depends(get_db),
):
    if request.method == "POST":
        if not title or not year or len(year) != 4 or len(title) > 60:
            request.state.msg = "Invalid input."
            return templates.TemplateResponse("index.html", {"request": request})
        new_movie = Movie(title=title, year=year)
        db.add(new_movie)
        db.commit()
        request.state.msg = "Item created."

    return templates.TemplateResponse("index.html", {"request": request})


@app.api_route("/settings", methods=["GET", "POST"])
def set_name(
    request: Request,
    name: str = Form(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(manager),
):
    if request.method == "POST":
        if not name or len(name) > 30:
            request.state.msg = "Invalid input."
            return templates.TemplateResponse("settings.html", {"request": request})

        db.execute(update(User).where(User.id == user.id).values(name=name))
        db.commit()
        request.state.user.name = name
        request.state.msg = "Settings updated."
        return templates.TemplateResponse("settings.html", {"request": request})

    return templates.TemplateResponse("settings.html", {"request": request})

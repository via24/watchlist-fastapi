from typing import Union

import bcrypt
from fastapi import APIRouter, Request, Response, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from ..database import SessionLocal
from ..dependencies import templates, manager
from ..models import User

router = APIRouter(tags=["auth"])


@manager.user_loader()
def query_user(user_email: str) -> Union[User, None]:
    with SessionLocal() as session:
        u = session.execute(
            select(User).where(User.email == user_email)
        ).scalar_one_or_none()
    return u


@router.get("/show_login")
def show_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login(
    request: Request, response: Response, data: OAuth2PasswordRequestForm = Depends()
):
    email = data.username
    if not email or not data.password:
        request.state.msg = "Invalid input."
        return templates.TemplateResponse("login.html", {"request": request})
    password = data.password.encode()

    user = query_user(email)
    if not user or not bcrypt.checkpw(password, user.hashed_password.encode()):
        request.state.msg = "Invalid username or password."
        return templates.TemplateResponse("login.html", {"request": request})

    access_token = manager.create_access_token(data={"sub": email})
    manager.set_cookie(response, access_token)
    request.state.msg = "Login success."
    request.state.user = user
    return RedirectResponse("/", status_code=302, headers=response.headers)
    # return templates.TemplateResponse(
    #     "index.html", {"request": request}, headers=response.headers
    # )


@router.get("/logout")
def logout(request: Request, response: Response, user: User = Depends(manager)):
    response.delete_cookie("access-token")

    request.state.msg = f"Goodbye. {user.name}"
    request.state.user = None
    return RedirectResponse("/", status_code=302, headers=response.headers)
    # return templates.TemplateResponse(
    #     "index.html", {"request": request}, headers=response.headers
    # )

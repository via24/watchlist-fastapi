from fastapi import APIRouter, HTTPException
from fastapi import Request, Response, Depends, Form
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from ..dependencies import get_db, templates, manager
from ..models import Movie, User

router = APIRouter(prefix="/movies", tags=["movies"])


@router.api_route("/edit/{movie_id}", methods=["GET", "POST"])
def edit_movie(
    request: Request,
    movie_id: int,
    title: str = Form(default=None),
    year: str = Form(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(manager),
):
    movie = db.execute(select(Movie).where(Movie.id == movie_id)).scalar_one_or_none()
    if not movie:
        raise HTTPException(404)

    if request.method == "POST":
        if not title or not year or len(year) != 4 or len(title) > 60:
            request.state.msg = "Invalid input."
            return templates.TemplateResponse(
                "edit.html", {"request": request, "movie": movie}
            )  # 重定向回对应的编辑页面
        movie.title, movie.year = title, year
        db.commit()
        db.refresh(movie)
        request.state.msg = "Item updated."

    return templates.TemplateResponse("edit.html", {"request": request, "movie": movie})


@router.post("/drop/{movie_id}")
def del_movie(
    request: Request,
    response: Response,
    movie_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(manager),
):
    db.execute(delete(Movie).where(Movie.id == movie_id))
    db.commit()
    request.state.msg = "Item deleted."
    return RedirectResponse("/", status_code=302, headers=response.headers)
    # return templates.TemplateResponse("index.html", {"request": request})

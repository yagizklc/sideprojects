from fastapi.routing import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from fastapi import Query
from sqlmodel import select
from typing import Annotated
from app.database import Session
from app.models import Title
from fastapi.templating import Jinja2Templates
from app.config import get_app_settings

settings = get_app_settings()
templates = Jinja2Templates(directory=settings.templates_path / "titles")

router = APIRouter()




@router.get("/titles", response_class=HTMLResponse, name="titles")
async def list_titles(request: Request, session: Session):
    query = select(Title)
    result = session.exec(query)
    titles = result.all()

    from collections import defaultdict

    titles_by_tag = defaultdict(list)
    for title in titles:
        for tag in title.tags:
            titles_by_tag[tag.name].append(title)

    return templates.TemplateResponse(
        "titles.html", {"request": request, "titles_by_tag": titles_by_tag}
    )


@router.get("/titles/{title_id}", name="title_detail", response_class=HTMLResponse)
async def get_title(request: Request, title_id: int, session: Session):
    query = select(Title).where(Title.id == title_id)
    result = session.exec(query)
    title = result.one()

    return templates.TemplateResponse(
        "title_detail.html", {"request": request, "title": title}
    )


@router.get("/movies/search", name="movie_search", response_class=HTMLResponse)
async def search(request: Request, session: Session, q: Annotated[str, Query()] = ""):
    raise NotImplementedError("Search is not implemented")

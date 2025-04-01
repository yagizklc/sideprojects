from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse
from fastapi.requests import Request
from fastapi import Query
from typing import Annotated
from app.config import get_app_settings
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.database import Session
from sqlmodel import select
from app.models import Episode

settings = get_app_settings()
templates = Jinja2Templates(directory=settings.templates_path / "player")
movies_path = settings.static_path / "movies"
router = APIRouter()


@router.get("/stream", name="stream")
def stream_video(
    request: Request,
    session: Session,
    q: Annotated[str, Query()] = "1",
):
    query = select(Episode).where(Episode.id == q)
    result = session.exec(query)
    episode = result.one()
    file_path = movies_path / f"{episode.name}.mp4"
    assert file_path.exists(), f"File {file_path} does not exist"

    def iterfile(file_name: str):
        with open(file_path, mode="rb") as file_like:
            yield from file_like

    return StreamingResponse(iterfile(q), media_type="video/mp4")


@router.get("/", response_class=HTMLResponse, name="player")
async def player(
    request: Request,
    session: Session,
    q: Annotated[str, Query()] = "1",
):
    query = select(Episode).where(Episode.id == q)
    result = session.exec(query)
    episode = result.one()

    return templates.TemplateResponse(
        "player.html",
        {
            "request": request,
            "video_file": q,
            "next": episode.next.id if episode.next else None,
            "previous": episode.previous.id if episode.previous else None,
        },
    )

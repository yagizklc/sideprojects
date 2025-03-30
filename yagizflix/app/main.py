from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import select

from app.database import Session
from app.models import Episode, Title

static_path = Path(__file__).parent / "static"
templates_path = Path(__file__).parent / "templates"
app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Initialize Jinja2 templates
templates = Jinja2Templates(directory=templates_path)


@app.get("/", response_class=HTMLResponse, name="home")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/titles", response_class=HTMLResponse, name="titles")
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


@app.get("/titles/{title_id}", name="title_detail", response_class=HTMLResponse)
async def get_title(request: Request, title_id: int, session: Session):
    query = select(Title).where(Title.id == title_id)
    result = session.exec(query)
    title = result.one()

    # get episodes for the title
    episodes = title.episodes

    # get the latest episode for the title
    for episode in episodes:
        if episode.first_episode():
            first_episode = episode
            break

    return templates.TemplateResponse(
        "title_detail.html", {"request": request, "title": title, "left_at": left_at}
    )


@app.get("/movies/search", name="movie_search", response_class=HTMLResponse)
async def search(request: Request, session: Session, q: Annotated[str, Query()] = ""):
    raise NotImplementedError("Search is not implemented")


@app.get("/stream", name="stream")
def stream_video(q: Annotated[str, Query()] = "sample.mp4"):
    def iterfile(file_name: str):
        # Ensure the file has .mp4 suffix
        if not file_name.lower().endswith(".mp4"):
            file_name = f"{file_name}.mp4"

        # Try to find the file in static directory
        file_path = static_path / "movies" / file_name

        # If file doesn't exist, fall back to sample.mp4
        if not file_path.exists():
            file_path = static_path / "movies" / "sample.mp4"
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="Video file not found")

        with open(file_path, mode="rb") as file_like:
            yield from file_like

    return StreamingResponse(iterfile(q), media_type="video/mp4")


@app.get("/player", response_class=HTMLResponse, name="player")
async def player(request: Request, q: Annotated[str, Query()] = "sample.mp4"):
    # In a real app, you would fetch movie details from a database
    return templates.TemplateResponse(
        "player.html", {"request": request, "video_file": q}
    )

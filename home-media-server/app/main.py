from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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


@app.get("/movies", response_class=HTMLResponse, name="movies")
async def movies(request: Request):
    # Sample movie data - in a real app, this would come from a database
    movies_by_category = {
        "Action": [
            {
                "id": 1,
                "title": "The Fast and Furious",
                "image": "https://via.placeholder.com/200x300",
            },
            {
                "id": 2,
                "title": "Mission Impossible",
                "image": "https://via.placeholder.com/200x300",
            },
            {
                "id": 3,
                "title": "Die Hard",
                "image": "https://via.placeholder.com/200x300",
            },
        ],
        "Comedy": [
            {
                "id": 4,
                "title": "The Hangover",
                "image": "https://via.placeholder.com/200x300",
            },
            {
                "id": 5,
                "title": "Superbad",
                "image": "https://via.placeholder.com/200x300",
            },
            {
                "id": 6,
                "title": "Bridesmaids",
                "image": "https://via.placeholder.com/200x300",
            },
        ],
        "Sci-Fi": [
            {
                "id": 7,
                "title": "Inception",
                "image": "https://via.placeholder.com/200x300",
            },
            {
                "id": 8,
                "title": "Interstellar",
                "image": "https://via.placeholder.com/200x300",
            },
            {
                "id": 9,
                "title": "The Matrix",
                "image": "https://via.placeholder.com/200x300",
            },
        ],
    }
    return templates.TemplateResponse(
        "movies.html", {"request": request, "movies_by_category": movies_by_category}
    )


@app.get("/movie/{movie_id}", name="movie_detail", response_class=HTMLResponse)
async def get_movie(request: Request, movie_id: int):
    # In a real app, you would fetch movie details from a database
    # For now, we'll use mock data
    movie = {
        "id": movie_id,
        "title": f"Movie {movie_id}",
        "description": "This is a sample movie description.",
        "image": "https://via.placeholder.com/400x600",
        "year": 2023,
        "director": "Sample Director",
    }
    return templates.TemplateResponse(
        "movie_detail.html", {"request": request, "movie": movie}
    )


@app.get("/stream", name="stream")
def stream_video(q: Annotated[str, Query()] = "sample.mp4"):
    def iterfile(file_name: str):
        # Ensure the file has .mp4 suffix
        if not file_name.lower().endswith(".mp4"):
            file_name = f"{file_name}.mp4"

        # Try to find the file in static directory
        file_path = static_path / file_name

        # If file doesn't exist, fall back to sample.mp4
        if not file_path.exists():
            file_path = static_path / "sample.mp4"
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

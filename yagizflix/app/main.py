from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates

from app.config import get_app_settings
from app.routers import player_router, titles_router
from app.database import create_db_and_tables

settings = get_app_settings()
templates = Jinja2Templates(directory=settings.templates_path)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    # populate_db()
    yield


app = FastAPI(lifespan=lifespan)

# Mount static files
app.mount(
    "/static", StaticFiles(directory=get_app_settings().static_path), name="static"
)

# register routers
app.include_router(player_router, prefix="/player")
app.include_router(titles_router, prefix="/titles")


# home page
@app.get("/", response_class=HTMLResponse, name="home")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

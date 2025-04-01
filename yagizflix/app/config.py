from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    base_path: Path = Path(__file__).parent
    templates_path: Path = base_path / "templates"
    static_path: Path = base_path / "static"


@lru_cache
def get_app_settings() -> AppSettings:
    return AppSettings()

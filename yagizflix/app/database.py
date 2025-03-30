from typing import Annotated
from fastapi import Depends
from sqlmodel import create_engine, Session as SQLModelSession

from .models import SQLModel

engine = create_engine("sqlite:///episodes.db")


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with SQLModelSession(engine) as session:
        yield session


Session = Annotated[SQLModelSession, Depends(get_session)]

from typing import Annotated

from fastapi import Depends
from sqlmodel import Session as SQLModelSession
from sqlmodel import create_engine

from .models import Episode, SQLModel, Tag, Title

engine = create_engine("sqlite:///episodes.db")


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with SQLModelSession(engine) as session:
        yield session


Session = Annotated[SQLModelSession, Depends(get_session)]


def populate_db():
    with SQLModelSession(engine) as session:
        # add title
        title = Title(name="Severance")
        session.add(title)
        session.commit()
        session.refresh(title)
        assert title.id is not None

        # add episodes
        episode3 = Episode(
            title_id=title.id,
            name="severances_s1e3",
        )
        session.add(episode3)
        session.commit()
        session.refresh(episode3)

        episode4 = Episode(
            title_id=title.id,
            name="severances_s1e4",
            previous_id=episode3.id,
        )
        episode3.next = episode4
        session.add(episode4)
        session.commit()
        session.refresh(episode4)
        session.refresh(episode3)

        episode5 = Episode(
            title_id=title.id,
            name="severances_s1e5",
            previous_id=episode4.id,
        )
        episode4.next = episode5
        session.add(episode5)
        session.commit()
        session.refresh(episode5)
        session.refresh(episode4)

        # add tags
        tag1 = Tag(name="drama")
        tag2 = Tag(name="mystery")
        tag3 = Tag(name="thriller")
        tag4 = Tag(name="ben stiller")

        session.add(tag1)
        session.add(tag2)
        session.add(tag3)
        session.add(tag4)
        session.commit()

        # link tags to title
        title.tags.append(tag1)
        title.tags.append(tag2)
        title.tags.append(tag3)
        title.tags.append(tag4)

        session.commit()

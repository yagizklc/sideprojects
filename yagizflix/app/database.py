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
        title = Title(name="Sample")
        session.add(title)
        session.commit()
        session.refresh(title)
        assert title.id is not None

        # add episodes
        episode1 = Episode(
            title_id=title.id,
            name="sample_s1e1",
        )
        session.add(episode1)
        session.commit()
        session.refresh(episode1)

        episode2 = Episode(
            title_id=title.id,
            name="sample_s1e2",
            previous_id=episode1.id,
        )
        episode1.next = episode2
        session.add(episode2)
        session.commit()
        session.refresh(episode2)
        session.refresh(episode1)

        episode3 = Episode(
            title_id=title.id,
            name="sample_s1e3",
            previous_id=episode2.id,
        )
        episode2.next = episode3
        session.add(episode3)
        session.commit()
        session.refresh(episode3)
        session.refresh(episode2)

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

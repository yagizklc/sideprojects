"""
Models for Movies and Episodes, and related tables

Keeps both movies and episodes in the same table, with a flag to indicate if it's a movie or an episode.

Desired features:
- able to continue watching an episode from where it was left
- go to next or previous episode
- search for a title by name, or by tag
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class TitleTagsLink(SQLModel, table=True):
    title_id: Optional[int] = Field(
        default=None, foreign_key="title.id", primary_key=True
    )
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)


class Title(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default="title name")
    watch_later: bool = Field(default=False)
    release_date: datetime = Field(default=datetime.now())

    # a list of tags that can be used to filter the title
    tags: list["Tag"] = Relationship(back_populates="titles", link_model=TitleTagsLink)

    # a list of episodes that can be used to navigate through the title
    episodes: list["Episode"] = Relationship(back_populates="title")


class Episode(SQLModel, table=True):
    """handles both series episodes and movies"""

    id: Optional[int] = Field(default=None, primary_key=True)

    # the title that the episode belongs to
    title_id: int = Field(foreign_key="title.id")
    title: Title = Relationship(back_populates="episodes")

    name: str = Field(default="episode name")

    # for previous and next navigation - or prequel and sequel
    previous_id: Optional[int] = Field(default=None, foreign_key="episode.id")
    next_id: Optional[int] = Field(default=None, foreign_key="episode.id")

    previous: Optional["Episode"] = Relationship(
        back_populates="next",
        sa_relationship_kwargs={
            "foreign_keys": "[Episode.previous_id]",
            "remote_side": "[Episode.id]",
        },
    )
    next: Optional["Episode"] = Relationship(
        back_populates="previous",
        sa_relationship_kwargs={"foreign_keys": "[Episode.next_id]"},
    )

    # for season and episode navigation
    season: int = Field(default=1, gt=0)
    episode_number: int = Field(default=1, gt=0)

    # for continue watching
    completed: bool = Field(default=False)
    left_at: Optional[int] = Field(default=None, gt=0)


class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default="tag name")
    description: str = Field(default="tag description")

    titles: list["Title"] = Relationship(
        back_populates="tags", link_model=TitleTagsLink
    )

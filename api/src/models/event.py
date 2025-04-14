"""Event model."""

from datetime import date, time

from sqlmodel import Field, SQLModel


class Event(SQLModel, table=True):
    """Event sql model class."""

    id: int | None = Field(default=None, primary_key=True)
    userId: str = Field(index=True)
    date: date
    time: time
    description: str

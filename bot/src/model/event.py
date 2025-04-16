"""Events model."""

from datetime import date, time

from pydantic import BaseModel


class EventModel(BaseModel):
    """Event model class."""

    id: int
    userId: str
    date: date
    time: time
    description: str

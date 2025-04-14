"""Event schemas."""

from datetime import date, time

from pydantic import BaseModel


class CreateEventSchema(BaseModel):
    """Create event schema."""

    userId: str
    date: date
    time: time
    description: str

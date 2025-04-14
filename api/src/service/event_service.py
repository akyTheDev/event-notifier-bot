"""Event service module."""

from datetime import date, time

from pydantic import InstanceOf, validate_call
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.core import NotFoundException
from src.models import Event


class EventService:
    """Event service class for CRUD event operations."""

    @validate_call
    async def create(
        self,
        userId: str,
        date: date,
        time: time,
        description: str,
        session: InstanceOf[AsyncSession],
    ) -> None:
        """Create a new event to the database.

        Arguments:
            userId: The user id to add a new event.
            date: The date of the event.
            time: The time of the event.
            description: The description of the event.
            session: The database session.

        Returns:
            None.
        """
        event: Event = Event(
            userId=userId, date=date, time=time, description=description
        )

        session.add(event)

    @validate_call
    async def get_events(
        self,
        session: InstanceOf[AsyncSession],
        userIds: list[str] | None = None,
        dates: list[date] | None = None,
    ) -> list[Event]:
        """Get events from the database.

        Arguments:
            session: The database session to connect to db.
            userIds: The user ids array to filter the db.
            dates: The dates array to filter db.

        Returns:
            The events of the given params.

        Raises:
            NotFoundException: If there is no event found.
        """
        query = select(Event)

        if userIds:
            query = query.where(Event.userId.in_(userIds))

        if dates:
            query = query.where(Event.date.in_(dates))

        result: list[Event] = list((await session.execute(query)).scalars().all())

        if not result:
            raise NotFoundException("Event not found!")

        return result

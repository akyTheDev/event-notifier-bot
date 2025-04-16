"""Unit tests for event service class."""


from pydantic import InstanceOf
import pytest

from datetime import date, time

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.core  import NotFoundException
from src.models import Event
from src.service.event_service import EventService

@pytest.fixture
def event_service() -> EventService:
    """Fixture of event service."""
    return EventService()

@pytest.fixture
def events() -> dict[int, Event]:
    event_1 = Event(
        userId="user1",
        description="event1",
        date=date(2025,1,1),
        time=time(1,1),
    )

    event_2 = Event(
        userId="user2",
        description="event2",
        date=date(2025,1,2),
        time=time(2,2),
    )

    event_3 = Event(
        userId="user3",
        description="event3",
        date=date(2025,1,3),
        time=time(3,3),
    )
    return {
        1:event_1,
        2:event_2,
        3:event_3,
    }

class TestCreateEvent:
    async def test_should_insert_correctly(self, event_service: EventService, db_session):
        await event_service.create(
            userId="user-unique-id-123",
            date=date(2025,1,3),
            time=time(12,13),
            description="test description",
            session=db_session
        )

        [result] = (await db_session.execute(select(Event).where(
            Event.userId == "user-unique-id-123"
        ))).fetchone()

        assert result.userId == "user-unique-id-123"
        assert result.date == date(2025,1,3)
        assert result.time == time(12,13)
        assert result.description == "test description"



class TestGetEvent:
    async def test_should_throw_not_found_error_if_no_row(self, event_service:EventService, db_session:InstanceOf[AsyncSession]):
        with pytest.raises(NotFoundException):
            await event_service.get_events(
                userIds=["user-no-123", "user-no-124"],
                session=db_session
            )


    async def test_should_return_events_by_filtering_user_ids(self, event_service:EventService, db_session:InstanceOf[AsyncSession], events):
        db_session.add(events[1])
        db_session.add(events[2])
        db_session.add(events[3])

        result = await event_service.get_events(
            session=db_session,
            userIds=["user1","user2"],
        )

        assert len(result) == 2

        event_result_1 = result[0]
        event_result_2 = result[1]
        assert events[1] == event_result_1
        assert events[2] == event_result_2


    async def test_should_return_events_by_filtering_dates(self, event_service:EventService, db_session:InstanceOf[AsyncSession], events):
        db_session.add(events[1])
        db_session.add(events[2])
        db_session.add(events[3])

        result = await event_service.get_events(
            session=db_session,
            start_date=date(2025,1,1),
            end_date=date(2025,1,2)
        )

        assert len(result) == 2

        event_result_1 = result[0]
        event_result_2 = result[1]
        assert events[1] == event_result_1
        assert events[2] == event_result_2


    async def test_should_return_events_by_filtering_dates_and_user_ids(self, event_service:EventService, db_session:InstanceOf[AsyncSession], events):
        db_session.add(events[1])
        db_session.add(events[2])
        db_session.add(events[3])

        result = await event_service.get_events(
            session=db_session,
            start_date=date(2025,1,2),
            end_date=date(2025,1,3),
            userIds=[
                'user1',
                "user3"
            ]

        )

        assert len(result) == 1

        event_result_1 = result[0]
        assert events[3] == event_result_1


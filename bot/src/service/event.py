"""Event service module."""

from datetime import date, time, timedelta
from typing import Any

from pydantic import validate_call

from src.core import configuration
from src.model import EventModel

from .utils import HTTPMethods, send_http_request


class EventService:
    """Event service class."""

    @validate_call
    async def create_new_event(
        self, telegram_id: int, date: date, time: time, description: str
    ) -> None:
        """Create a new event by sending an http request to the api.

        Arguments:
            telegram_id: Telegram id of the users.
            date: The date of the event.
            time: The time of the event.
            description: The description of the event.

        Return:
            None.
        """
        await send_http_request(
            url=str(configuration.API.URL) + "event/",
            body={
                "userId": str(telegram_id),
                "date": str(date),
                "time": str(time),
                "description": description,
            },
            method=HTTPMethods.POST,
        )

    @validate_call
    async def get_events_by_user(
        self, telegram_id: int, day: int
    ) -> dict[date, list[EventModel]]:
        """Get the events of the user after sorting by date and time.

        Arguments:
            telegram_id: Telegram id to filter events.
            day: The day filter.

        Returns:
            The sorted events of the user.
        """
        start_date: date = date.today()
        end_date: date = start_date + timedelta(days=day)
        response: list[dict[str, Any]] = await send_http_request(
            url=str(configuration.API.URL) + "event/",
            params={
                "userIds": telegram_id,
                "start_date": start_date,
                "end_date": end_date,
            },
        )

        result: dict[date, list[EventModel]] = {}
        for event_raw in response:
            event: EventModel = EventModel(**event_raw)
            if event.date not in result:
                result[event.date] = []
            result[event.date].append(event)

        for d in result:
            result[d].sort(key=lambda e: e.time)

        return result

    @validate_call
    async def get_all_events_of_date(
        self, event_date: date
    ) -> dict[str, list[EventModel]]:
        """Get all events of the given date.

        Arguments:
            event_date: Event date to fetch events.

        Returns:
            The events which are grouped by users.
        """
        response: list[dict[str, Any]] = await send_http_request(
            url=str(configuration.API.URL) + "event/",
            params={
                "start_date": event_date,
                "end_date": event_date,
            },
        )

        result: dict[str, list[EventModel]] = {}
        for event_raw in response:
            event: EventModel = EventModel(**event_raw)
            if event.userId not in result:
                result[event.userId] = []
            result[event.userId].append(event)

        return result

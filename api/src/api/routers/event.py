"""Event router."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel, Field

from src.models import Event
from src.schemas import CreateEventSchema
from src.service import EventService, ServiceFactory

from ..deps import SessionDep

event_router: APIRouter = APIRouter(prefix="/event", tags=["event"])

event_service: EventService = ServiceFactory.create_event_service()


@event_router.post("/", summary="Get events.", status_code=201)
async def create_event(
    create_model: Annotated[CreateEventSchema, Body(...)],
    session: SessionDep,
):
    """Create a new event by using the given input."""
    await event_service.create(
        userId=create_model.userId,
        time=create_model.time,
        date=create_model.date,
        description=create_model.description,
        session=session,
    )

    return ORJSONResponse(content=jsonable_encoder({"message": "ok"}), status_code=201)


class GetEventsDependencies(BaseModel):
    """Get events dependencies."""

    userIds: list[str] | None = Field(
        Query(default=None, description="List of user IDs to filter events by")
    )

    dates: list[date] | None = Field(
        Query(
            default=None,
            description="List of dates (in YYYY-MM-DD format) to filter events by",
        )
    )


@event_router.get(
    "/", summary="Get events.", status_code=200, response_model=list[Event]
)
async def get_events(
    session: SessionDep, params: Annotated[GetEventsDependencies, Depends()]
):
    """Get events by filtering the given params."""
    result = await event_service.get_events(
        session=session, userIds=params.userIds, dates=params.dates
    )

    return ORJSONResponse(content=jsonable_encoder(result), status_code=200)

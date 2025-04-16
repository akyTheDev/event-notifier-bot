"""Celery scheduler module."""

import asyncio
import logging
from datetime import date

from aiogram import Bot

from model.event import EventModel
from src.core import configuration
from src.service import EventService, ServiceFactory

logging.basicConfig(level=logging.INFO)


async def handle_user_events(
    bot: Bot, event_date: date, telegram_id: str, events: list[EventModel]
) -> None:
    """Handle the user's event by notifying."""
    lines: list[str] = [
        f"<b>Hey!!! Good morning!</b> I'm here to list your today's events!\n\n"
        f"<b>{event_date}</b> – {len(events)} "
        f"event{'s' if len(events) != 1 else ''} 📅\n"
    ]

    for event in events:
        lines.append(f"  • {event.description}  ⏰ {event.time}")

    await bot.send_message(
        chat_id=telegram_id, text="\n".join(lines), parse_mode="HTML"
    )


async def main():
    """Run the main celery."""
    event_service: EventService = ServiceFactory.create_event_service()
    bot: Bot = Bot(token=configuration.TELEGRAM_TOKEN)

    today = date.today()
    result: dict[str, list[EventModel]] = await event_service.get_all_events_of_date(
        event_date=today,
    )

    for telegram_id in result:
        await handle_user_events(
            bot=bot,
            event_date=today,
            telegram_id=telegram_id,
            events=result[telegram_id],
        )

    await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

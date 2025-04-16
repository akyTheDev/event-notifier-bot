"""Module to store the Celery tasks."""

import asyncio
import logging
from datetime import date

from aiogram import Bot
from celery import Celery
from celery.schedules import crontab

from src.core import configuration
from src.model import EventModel
from src.service import EventService, ServiceFactory

logging.basicConfig(level=logging.INFO)

celery: Celery = Celery(
    "celery-app",
    broker=f"redis://:{configuration.REDIS.PASS}@"
    f"{configuration.REDIS.HOST}:{str(configuration.REDIS.PORT)}/0",
)


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


@celery.task
def send_daily_message():
    """Task to send daily message."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Setup periodic tasks."""
    sender.add_periodic_task(
        crontab(hour="6", minute="0"),
        send_daily_message.s(),
        name="Daily messages",
    )

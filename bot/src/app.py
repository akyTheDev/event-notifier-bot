"""Main app file."""

import asyncio
import logging
from calendar import month_name, monthcalendar
from datetime import date, datetime, time
from typing import Final

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from src.core import configuration
from src.model import EventModel
from src.service import EventService, ServiceFactory

logging.basicConfig(level=logging.INFO)

bot: Bot = Bot(token=configuration.TELEGRAM_TOKEN)
dp: Dispatcher = Dispatcher()
logger: logging.Logger = logging.getLogger()

event_service: EventService = ServiceFactory.create_event_service()


class EventCreation(StatesGroup):
    """Event creation state group."""

    waiting_for_event_name: State = State()
    waiting_for_event_time: State = State()


def generate_calendar_view(year: int, month: int) -> InlineKeyboardMarkup:
    """Generate a calendar view by using the given year and month.

    Arguments:
        year: Year to generate a monthly view.
        month: Month to generate a monthly view.

    Returns:
        The calendar formatted buttons of telegram.
    """
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[])
    header = [
        InlineKeyboardButton(text=f"{month_name[month]} {year}", callback_data="ignore")
    ]
    keyboard.inline_keyboard.append(header)

    weekdays: tuple[str, ...] = ("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su")
    keyboard.inline_keyboard.append(
        [InlineKeyboardButton(text=day, callback_data="ignore") for day in weekdays]
    )

    month_calendar: list[list[int]] = monthcalendar(year, month)
    for week in month_calendar:
        row: list[InlineKeyboardButton] = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            else:
                row.append(
                    InlineKeyboardButton(
                        text=str(day), callback_data=f"create_{year}_{month}_{day}"
                    )
                )
        keyboard.inline_keyboard.append(row)

    prev_year, prev_month = (year, month - 1) if month > 1 else (year - 1, 12)
    next_year, next_month = (year, month + 1) if month < 12 else (year + 1, 1)

    keyboard.inline_keyboard.append(
        [
            InlineKeyboardButton(
                text="<", callback_data=f"prev_{prev_year}_{prev_month}"
            ),
            InlineKeyboardButton(text="Cancel", callback_data="cancel"),
            InlineKeyboardButton(
                text=">", callback_data=f"next_{next_year}_{next_month}"
            ),
        ]
    )

    return keyboard


welcome_text: Final[str] = (
    "<b>Hey!</b> Welcome to <b>Event Reminder Bot</b>!\n\n"
    "Use the menu below to get started:\n"
    "➕ <i>Create</i> – Schedule a new event (/create)\n"
    "📅 <i>Events</i> – List your upcoming events (/events)\n"
    "❓ <i>Help</i> – Show this menu again (/help)\n"
)


@dp.message(Command("create"))
async def create_handler(message: Message):
    """Handle the `/create` command.

    Prints the selectable calendar.
    """
    now: datetime = datetime.now()
    markup: InlineKeyboardMarkup = generate_calendar_view(now.year, now.month)
    await message.answer("Select a date:", reply_markup=markup)


@dp.callback_query(
    lambda c: c.data is not None
    and (c.data.startswith("prev_") or c.data.startswith("next_"))
)
async def nav_callback(callback_query: types.CallbackQuery):
    """Handles the calendar navigation callbacks.

    Changes the view of the calendar according to the selected button.
    """
    if not callback_query.data or not callback_query.message:
        logger.error(f"[nav_callback]: {callback_query}'s data or message is empty.")
        return

    parts: list[str] = callback_query.data.split("_")
    year: int = int(parts[1])
    month: int = int(parts[2])
    new_markup = generate_calendar_view(year, month)
    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=new_markup,
    )
    await bot.answer_callback_query(callback_query.id)


@dp.callback_query(lambda c: c.data == "cancel")
async def cancel_callback(callback_query: types.CallbackQuery):
    """Close the calendar view."""
    if not callback_query.message:
        logger.error(f"[cancel_callback]: {callback_query}'s message is empty.")
        return
    await bot.answer_callback_query(callback_query.id, text="Selection canceled.")
    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=None,
    )


@dp.callback_query(lambda c: c.data is not None and c.data.startswith("create_"))
async def crate_day_callback(callback_query: types.CallbackQuery, state: FSMContext):
    """Callback that is triggered by date selection.

    Firstly, generate the event date by using the selected date. Then, set the date to
    the state since it will be used from other callback. Also, removes the calendar view
    and prints the selected date. Lastly, ask for the event name.
    """
    if not callback_query.data or not callback_query.message:
        logger.error(
            f"[create_day_callback]: {callback_query}'s data or message is empty."
        )
        return

    _, year, month, day = callback_query.data.split("_")
    event_date: date = date(int(year), int(month), int(day))
    await state.update_data(event_date=event_date)
    await bot.answer_callback_query(
        callback_query.id, text=f"Date selected: {event_date}"
    )

    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=f"Selected date: {event_date}",
    )

    await bot.send_message(callback_query.from_user.id, "Please enter the event name:")
    await state.set_state(EventCreation.waiting_for_event_name)


@dp.message(EventCreation.waiting_for_event_name)
async def create_event_name_handler(message: Message, state: FSMContext):
    """Handle event name selection."""
    await state.update_data(event_name=message.text)
    await message.answer("Please enter the event time (e.g., HH:MM):")
    await state.set_state(EventCreation.waiting_for_event_time)


@dp.message(EventCreation.waiting_for_event_time)
async def event_time_handler(message: Message, state: FSMContext):
    """Handle event time selection."""
    try:
        if not message.text or not message.from_user:
            raise ValueError()
        validated_time: time = datetime.strptime(message.text, "%H:%M").time()
    except ValueError:
        await message.answer("Please enter a valid time in HH:MM format, e.g., 14:30.")
        return

    await state.update_data(event_time=validated_time)
    data = await state.get_data()

    event_date: date = data.get("event_date")
    event_name: str = data.get("event_name")
    event_time: time = data.get("event_time")

    await event_service.create_new_event(
        telegram_id=message.from_user.id,
        date=event_date,
        time=event_time,
        description=event_name,
    )

    # Send a summary message back to the user.
    await message.answer(
        f"Your event details:\n"
        f"Date: {event_date}\n"
        f"Name: {event_name}\n"
        f"Time: {event_time}"
    )

    await state.clear()


@dp.message(Command("events"))
async def handle_show_events(message: Message, state: FSMContext):
    """Handle show list events command."""
    if not message.from_user:
        logger.error(f"[show_events_handler]: {message}'s from_user is empty.")
        return

    telegram_id = message.from_user.id
    events: dict[date, list[EventModel]] = await event_service.get_events_by_user(
        telegram_id=telegram_id, day=7
    )

    if not events:
        await message.answer("You have no events planned. Try adding one with /create!")
        return

    await state.update_data(events=events)

    lines = ["<b>📆 Your Upcoming Events:</b>\n"]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    for event_date in sorted(events.keys()):
        events_list = events[event_date]
        # Create a summary line for the date:
        lines.append(
            f"<b>{event_date}</b> – {len(events_list)} "
            f"event{'s' if len(events_list) != 1 else ''} 📅"
        )
        lines.append("<i>(Click the button below to show details)</i>\n")

        # Add a toggle button for this date group.
        # The callback_data is set to something like "toggle_2025-04-04"
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"Show details for {event_date}",
                    callback_data=f"toggle_{event_date}",
                )
            ]
        )

    response_text = "\n".join(lines)

    await message.answer(response_text, parse_mode="HTML", reply_markup=keyboard)


@dp.callback_query(lambda c: c.data and c.data.startswith("toggle_"))
async def toggle_details_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle date details."""
    if not callback_query.data or not callback_query.message:
        logger.error(
            f"[toggle_details_handler]: {callback_query}'s data or message is empty."
        )
        return
    event_date_str: str = callback_query.data.split("_", 1)[1]

    data = await state.get_data()
    events = data.get("events", {})

    event_date: date = date.fromisoformat(event_date_str)
    events_list: list[EventModel] = events.get(event_date)
    if not events_list:
        await callback_query.answer("No events for this date", show_alert=True)
        return

    lines = [
        f"<b>{event_date}</b> – {len(events_list)} "
        f"event{'s' if len(events_list) != 1 else ''} 📅"
    ]

    for event in events_list:
        lines.append(f"  • {event.description}  ⏰ {event.time}")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"Selected date: {event_date}",
                    callback_data="ignore",
                )
            ]
        ]
    )

    await callback_query.message.edit_text(  # type: ignore
        "\n".join(lines), parse_mode="HTML", reply_markup=keyboard
    )
    await callback_query.answer()


@dp.message(Command("start"))
async def handle_start(message: Message):
    """Handle the `/start` command.

    Prints the start menu.
    """
    await message.answer(welcome_text, parse_mode="HTML")


@dp.message(Command("help"))
async def handle_help(message: Message):
    """Handle the `/help` command.

    Prints the start menu.
    """
    await message.answer(welcome_text, parse_mode="HTML")


async def main():
    """Run the telegram bot."""
    logger.info("Bot started")
    await dp.start_polling(bot)
    logger.info("Bot started")


if __name__ == "__main__":
    asyncio.run(main())

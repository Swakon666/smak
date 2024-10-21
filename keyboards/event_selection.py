# keyboards/event_selection.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils.db_api import get_all_events

async def get_event_selection_keyboard():
    events = await get_all_events()
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    
    for event in events:
        button = KeyboardButton(event.title)
        keyboard.add(button)
    
    keyboard.add(KeyboardButton("Отмена"))
    return keyboard

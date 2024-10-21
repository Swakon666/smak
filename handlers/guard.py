 # handlers/guard.py
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from config import ADMIN_IDS  # Импортируйте ADMIN_IDS для проверки прав доступа

async def guard_panel(message: types.Message):
    # Проверка на администратора или охранника
    if message.from_user.id in ADMIN_IDS:
        await message.reply("Панель охранника доступна.")
    else:
        await message.reply("У вас нет доступа к панели охранника.")

def register_guard_handlers(dp: Dispatcher):
    # Регистрация команды /guard для охранников
    dp.register_message_handler(guard_panel, commands=["guard"], state="*")


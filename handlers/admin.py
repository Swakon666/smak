 # handlers/admin.py
from aiogram import types, Dispatcher
from config import ADMIN_IDS  # Импортируем ADMIN_IDS из config.py

async def admin_panel(message: types.Message):
    # Проверка, чтобы убедиться, что сообщение пришло от администратора
    if message.from_user.id in ADMIN_IDS:
        await message.reply("Добро пожаловать в панель администратора!")
    else:
        await message.reply("У вас нет доступа к панели администратора.")

def register_admin_handlers(dp: Dispatcher):
    # Регистрация обработчика команды /admin
    dp.register_message_handler(admin_panel, commands=["admin"], state="*")


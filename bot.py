import logging
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage  # Добавим хранилище состояний
from config import BOT_TOKEN
import asyncio
from handlers import setup_handlers
from aiogram import Bot, Dispatcher, executor, types
from config import BOT_TOKEN
from utils.db_api import init_db
from handlers import setup_handlers
# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера с хранилищем для FSM
storage = MemoryStorage()  # Хранилище для состояний в памяти
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)  # Подключаем storage для состояний

# Функция, выполняющаяся при старте бота
@dp.message_handler(commands=['start'])
async def send_welcome(message):
    await message.reply("Добро пожаловать в бот Smak! Пожалуйста, зарегистрируйтесь, используя команду /register.")

# Регистрация всех обработчиков
setup_handlers(dp)

# Функция для инициализации базы данных при запуске
async def on_startup(dp):
    await init_db()
    logging.info("База данных успешно инициализирована.")

# Функция для корректного завершения работы бота
async def on_shutdown(dp):
    logging.info("Бот останавливается. Закрытие базы данных...")
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.info("Все соединения успешно закрыты.")

# Запуск бота с корректной обработкой событийного цикла
if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
    


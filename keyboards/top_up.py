# keyboards/top_up.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Определение кнопок выбора банка
button_tinkoff = KeyboardButton("Тинькофф")
button_sberbank = KeyboardButton("Сбербанк")
button_cancel = KeyboardButton("Отмена")

# Создание клавиатуры выбора банка
bank_selection_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [button_tinkoff, button_sberbank],
        [button_cancel]
    ],
    resize_keyboard=True
)

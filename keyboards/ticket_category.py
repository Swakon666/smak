# keyboards/ticket_category.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Определение кнопок категорий билета
button_standard = KeyboardButton("Standard")
button_premium = KeyboardButton("Premium")
button_vip = KeyboardButton("VIP")
button_cancel = KeyboardButton("Отмена")

# Создание клавиатуры выбора категории билета
ticket_category_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [button_standard, button_premium, button_vip],
        [button_cancel]
    ],
    resize_keyboard=True
)

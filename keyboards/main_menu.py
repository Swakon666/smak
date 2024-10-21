 # keyboards/main_menu.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Определение кнопок
button_top_up = KeyboardButton("Пополнить баланс")
button_buy_ticket = KeyboardButton("Купить билет")
button_view_balance = KeyboardButton("Мой баланс")
button_bar_menu = KeyboardButton("Барная карта")
button_support = KeyboardButton("Поддержка")

# Создание клавиатуры
main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [button_top_up, button_buy_ticket],
        [button_view_balance, button_bar_menu],
        [button_support]
    ],
    resize_keyboard=True
)


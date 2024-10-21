# handlers/tickets.py
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from states.ticket_states import TicketPurchaseStates
from keyboards.event_selection import get_event_selection_keyboard
from keyboards.ticket_category import ticket_category_keyboard
from keyboards.main_menu import main_menu_keyboard  # Убедитесь, что импортирован
from utils.db_api import (
    get_user_by_telegram_id, 
    get_all_events, 
    get_event_by_title, 
    check_user_balance, 
    deduct_balance,  # Убедитесь, что эта строка присутствует
    create_ticket, 
    get_ticket_price, 
    get_event_title
)
from utils.qr_generator import generate_qr_code  # Убедитесь, что функция определена
from utils.payment import check_payment_status  # Добавлен импорт
import asyncio
import logging

async def buy_ticket_start(message: types.Message):
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.reply("Вы не зарегистрированы. Пожалуйста, зарегистрируйтесь, используя команду /register.")
        return
    
    events_keyboard = await get_event_selection_keyboard()
    if not events_keyboard.keyboard[0]:
        await message.reply("На данный момент нет доступных мероприятий.")
        return
    
    await message.reply("Выберите мероприятие:", reply_markup=events_keyboard)
    await TicketPurchaseStates.waiting_for_event_selection.set()

async def select_event(message: types.Message, state: FSMContext):
    selected_event_title = message.text
    if selected_event_title == "Отмена":
        await message.reply("Покупка билета отменена.", reply_markup=main_menu_keyboard)
        await state.finish()
        return
    
    event = await get_event_by_title(selected_event_title)
    if not event:
        await message.reply("Мероприятие не найдено. Пожалуйста, выберите мероприятие из списка.", reply_markup=await get_event_selection_keyboard())
        return
    
    await state.update_data(event_id=event.id, selected_event_title=selected_event_title)  # Сохраняем заголовок события
    await message.reply("Выберите категорию билета:", reply_markup=ticket_category_keyboard)
    await TicketPurchaseStates.waiting_for_ticket_category.set()

async def select_ticket_category(message: types.Message, state: FSMContext):
    selected_category = message.text
    if selected_category == "Отмена":
        await message.reply("Покупка билета отменена.", reply_markup=main_menu_keyboard)
        await state.finish()
        return
    
    if selected_category not in ["Standard", "Premium", "VIP"]:
        await message.reply("Пожалуйста, выберите категорию билета из списка.", reply_markup=ticket_category_keyboard)
        return
    
    user_data = await state.get_data()
    event_id = user_data.get('event_id')

    # Получение цены билета
    ticket_price = await get_ticket_price(event_id, selected_category)
    
    await state.update_data(ticket_category=selected_category, ticket_price=ticket_price)
    
    await message.reply(f"Вы выбрали категорию **{selected_category}**. Цена: {ticket_price} Smak-коинов.\n\n"
                        f"Подтвердите покупку билета?", 
                        reply_markup=confirmation_keyboard())
    await TicketPurchaseStates.waiting_for_confirmation.set()

async def confirm_purchase(message: types.Message, state: FSMContext):
    if message.text.lower() not in ["да", "нет"]:
        await message.reply("Пожалуйста, ответьте 'Да' или 'Нет'.")
        return
    
    if message.text.lower() == "нет":
        await message.reply("Покупка билета отменена.", reply_markup=main_menu_keyboard)
        await state.finish()
        return
    
    user_data = await state.get_data()
    event_id = user_data.get('event_id')
    ticket_category = user_data.get('ticket_category')
    ticket_price = user_data.get('ticket_price')
    selected_event_title = user_data.get('selected_event_title')  # Получаем заголовок события из состояния
    
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.reply("Вы не зарегистрированы. Пожалуйста, зарегистрируйтесь, используя команду /register.")
        await state.finish()
        return
    
    # Проверка баланса
    has_balance = await check_user_balance(user.id, ticket_price)
    if not has_balance:
        await message.reply("Недостаточно средств на балансе. Пожалуйста, пополните баланс.", reply_markup=main_menu_keyboard)
        await state.finish()
        return
    
    # Списание средств
    await deduct_balance(user.id, ticket_price)
    
    # Генерация QR-кода билета
    qr_code_path = await generate_qr_code(user.id, event_id, ticket_category)
    
    # Создание записи билета в базе данных
    ticket = await create_ticket(user.id, event_id, ticket_category, qr_code_path)
    
    if not ticket:
        await message.reply("Не удалось приобрести билет. Возможно, билетов больше нет.", reply_markup=main_menu_keyboard)
        await state.finish()
        return
    
    # Получение названия мероприятия
    event_title = await get_event_title(event_id)
    
    # Отправка билета пользователю
    with open(qr_code_path, 'rb') as qr_file:
        await message.reply_photo(qr_file, caption=f"🎟 **Ваш билет на мероприятие:**\n\n"
                                                   f"**Мероприятие:** {event_title}\n"
                                                   f"**Категория:** {ticket_category}\n"
                                                   f"**QR-код:** Сохраните этот QR-код для входа на мероприятие.",
                                 reply_markup=main_menu_keyboard)
    
    logging.info(f"Пользователь {user.id} приобрёл билет на мероприятие '{event_title}' категории '{ticket_category}'.")
    await state.finish()

def confirmation_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Да"))
    keyboard.add(types.KeyboardButton("Нет"))
    return keyboard

def register_ticket_handlers(dp: Dispatcher):
    dp.register_message_handler(buy_ticket_start, Text(equals="Купить билет"), state='*')
    dp.register_message_handler(select_event, state=TicketPurchaseStates.waiting_for_event_selection, content_types=types.ContentTypes.TEXT)
    dp.register_message_handler(select_ticket_category, state=TicketPurchaseStates.waiting_for_ticket_category, content_types=types.ContentTypes.TEXT)
    dp.register_message_handler(confirm_purchase, state=TicketPurchaseStates.waiting_for_confirmation, content_types=types.ContentTypes.TEXT)

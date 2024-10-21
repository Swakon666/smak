# handlers/top_up.py
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from states.top_up_states import TopUpStates
from keyboards.top_up import bank_selection_keyboard
from keyboards.main_menu import main_menu_keyboard
from utils.db_api import get_user_by_telegram_id, update_balance
from utils.payment import get_payment_details, check_payment_status
import asyncio
import logging

async def select_bank(message: types.Message, state: FSMContext):
    selected_bank = message.text
    if selected_bank == "Тинькофф":
        bank = "Tinkoff"
    elif selected_bank == "Сбербанк":
        bank = "Sberbank"
    elif selected_bank == "Отмена":
        await message.reply("Пополнение баланса отменено.", reply_markup=main_menu_keyboard)
        await state.finish()
        return
    else:
        await message.reply("Пожалуйста, выберите банк из предложенных вариантов.", reply_markup=bank_selection_keyboard)
        return
    
    # Сохранение выбранного банка в состоянии
    await state.update_data(bank=bank)
    
    # Получение реквизитов для оплаты через крипто-бота
    payment_details = await get_payment_details(bank)
    
    if not payment_details:
        await message.reply("Не удалось получить реквизиты для оплаты. Попробуйте позже.", reply_markup=main_menu_keyboard)
        await state.finish()
        return
    
    # Сохранение payment_details в состоянии
    await state.update_data(payment_details=payment_details)
    
    # Отправка реквизитов пользователю
    payment_info = (
        f"**Реквизиты для оплаты через {bank}:**\n\n"
        f"**Номер счета:** {payment_details['account_number']}\n"
        f"**БИК:** {payment_details['bik']}\n"
        f"**Наименование банка:** {payment_details['bank_name']}\n\n"
        f"**Комментарий к переводу:** {payment_details['comment']}\n\n"
        f"Пожалуйста, выполните перевод в течение 10 минут и нажмите кнопку **'Подтвердить перевод'**."
    )
    
    # Создание кнопки подтверждения перевода
    confirm_button = types.ReplyKeyboardMarkup(resize_keyboard=True)
    confirm_button.add(types.KeyboardButton("Подтвердить перевод"))
    confirm_button.add(types.KeyboardButton("Отмена"))
    
    await message.reply(payment_info, reply_markup=confirm_button)
    
    # Сохранение времени начала перевода
    await state.update_data(start_time=asyncio.get_event_loop().time())
    
    await TopUpStates.waiting_for_confirmation.set()

async def confirm_payment(message: types.Message, state: FSMContext):
    if message.text != "Подтвердить перевод":
        if message.text == "Отмена":
            await message.reply("Пополнение баланса отменено.", reply_markup=main_menu_keyboard)
            await state.finish()
            return
        else:
            await message.reply("Пожалуйста, нажмите кнопку 'Подтвердить перевод' или 'Отмена'.")
            return
    
    user_data = await state.get_data()
    bank = user_data.get('bank')
    payment_details = user_data.get('payment_details')  # Извлечение payment_details
    start_time = user_data.get('start_time')
    
    current_time = asyncio.get_event_loop().time()
    elapsed_time = current_time - start_time
    
    if elapsed_time > 600:  # 10 минут = 600 секунд
        await message.reply("Время для подтверждения перевода истекло.", reply_markup=main_menu_keyboard)
        await state.finish()
        return
    
    # Проверка статуса перевода через крипто-бота
    payment_status = await check_payment_status(user_data, bank)
    
    if payment_status:
        # Обновление баланса пользователя
        amount = payment_details['amount']  # Теперь payment_details определена
        await update_balance(message.from_user.id, amount)
        await message.reply(f"Баланс успешно пополнен на {amount} Smak-коинов.", reply_markup=main_menu_keyboard)
        logging.info(f"Баланс пользователя {message.from_user.id} пополнен на {amount} Smak-коинов.")
    else:
        await message.reply("Не удалось подтвердить перевод. Пожалуйста, попробуйте позже.", reply_markup=main_menu_keyboard)
        logging.warning(f"Не удалось подтвердить перевод для пользователя {message.from_user.id}.")
    
    await state.finish()

async def cancel_top_up(message: types.Message, state: FSMContext):
    await message.reply("Пополнение баланса отменено.", reply_markup=main_menu_keyboard)
    await state.finish()

def register_top_up_handlers(dp: Dispatcher):
    dp.register_message_handler(select_bank, state=TopUpStates.waiting_for_bank, content_types=types.ContentTypes.TEXT)
    dp.register_message_handler(confirm_payment, Text(equals="Подтвердить перевод"), state=TopUpStates.waiting_for_confirmation)
    dp.register_message_handler(cancel_top_up, Text(equals="Отмена"), state=TopUpStates.waiting_for_confirmation)

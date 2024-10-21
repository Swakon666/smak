from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from states.registration_states import RegistrationStates
from utils.db_api import add_user, get_user_by_telegram_id
from aiogram.dispatcher.filters import Text
from keyboards.main_menu import main_menu_keyboard
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from states.registration_states import RegistrationStates
from utils.db_api import add_user, get_user_by_telegram_id
from aiogram.dispatcher.filters import Command
from states.top_up_states import TopUpStates
from keyboards.top_up import bank_selection_keyboard


async def register_start(message: types.Message):
    user = await get_user_by_telegram_id(message.from_user.id)
    if user:
        await message.reply("Вы уже зарегистрированы.")
    else:
        await message.reply("Пожалуйста, введите ваше имя:")
        await RegistrationStates.waiting_for_name.set()

MAX_NAME_LENGTH = 50

async def process_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if len(name) > MAX_NAME_LENGTH:
        await message.reply(f"Имя слишком длинное. Максимальная длина: {MAX_NAME_LENGTH} символов. Попробуйте снова.")
        return
    await state.update_data(name=name)
    await message.reply("Пожалуйста, введите ваш возраст (не менее 18 лет):")
    await RegistrationStates.waiting_for_age.set()

# Добавляем функцию process_age
async def process_age(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        if age < 18:
            await message.reply("Извините, регистрация доступна только пользователям старше 18 лет.")
            await state.finish()
            return
        await state.update_data(age=age)
        await message.reply("Пожалуйста, введите ваше учебное заведение или организацию:")
        await RegistrationStates.waiting_for_institution.set()
    except ValueError:
        await message.reply("Пожалуйста, введите корректный возраст (число):")

MAX_INSTITUTION_LENGTH = 100

async def process_institution(message: types.Message, state: FSMContext):
    institution = message.text.strip()
    if len(institution) > MAX_INSTITUTION_LENGTH:
        await message.reply(f"Название учебного заведения/организации слишком длинное. Максимальная длина: {MAX_INSTITUTION_LENGTH} символов. Попробуйте снова.")
        return
    user_data = await state.get_data()
    await add_user(
        telegram_id=message.from_user.id,
        name=user_data['name'],
        age=user_data['age'],
        institution=institution
    )
    await message.reply("Регистрация прошла успешно! Ваш баланс Smak-коинов: 0.", reply_markup=main_menu_keyboard)
    await state.finish()

async def view_balance(message: types.Message):
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.reply("Вы не зарегистрированы. Пожалуйста, зарегистрируйтесь, используя команду /register.")
        return
    await message.reply(f"Ваш текущий баланс: {user.smak_coin} Smak-коинов.")

async def send_main_menu(message: types.Message):
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.reply("Вы не зарегистрированы. Пожалуйста, зарегистрируйтесь, используя команду /register.")
        return
    await message.reply("Выберите действие из меню ниже:", reply_markup=main_menu_keyboard)

async def handle_main_menu_selection(message: types.Message):
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.reply("Вы не зарегистрированы. Пожалуйста, зарегистрируйтесь, используя команду /register.")
        return
    
async def handle_main_menu_selection(message: types.Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.reply("Вы не зарегистрированы. Пожалуйста, зарегистрируйтесь, используя команду /register.")
        return
    
    text = message.text
    if text == "Пополнить баланс":
        await message.reply("Выберите банк для перевода:", reply_markup=bank_selection_keyboard)
        await TopUpStates.waiting_for_bank.set()
    elif text == "Купить билет":
        await message.reply("Функция покупки билета ещё не реализована.")
        # Здесь будет вызов функции покупки билета
    elif text == "Мой баланс":
        await view_balance(message)
    elif text == "Барная карта":
        await message.reply("Функция просмотра барной карты ещё не реализована.")
        # Здесь будет вызов функции просмотра барной карты
    elif text == "Поддержка":
        await message.reply("Свяжитесь с поддержкой по адресу support@example.com или используйте команду /contact.")
    else:
        await message.reply("Пожалуйста, выберите действие из меню.", reply_markup=main_menu_keyboard)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(register_start, commands=['register'], state='*')
    dp.register_message_handler(process_name, state=RegistrationStates.waiting_for_name)
    dp.register_message_handler(process_age, state=RegistrationStates.waiting_for_age)
    dp.register_message_handler(process_institution, state=RegistrationStates.waiting_for_institution)
    dp.register_message_handler(view_balance, commands=['balance'], state='*')
    dp.register_message_handler(send_main_menu, commands=['menu'], state='*')
    dp.register_message_handler(handle_main_menu_selection, Text(equals=["Пополнить баланс", "Купить билет", "Мой баланс", "Барная карта", "Поддержка"]), state='*')
